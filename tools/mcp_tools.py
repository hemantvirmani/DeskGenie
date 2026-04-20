"""MCP (Model Context Protocol) tool loader.

Loads LangChain-compatible tools from all configured MCP servers defined in
the ``mcpServers`` section of config.json.
Adding a new MCP server requires only a single config.json entry — tools are
auto-discovered at startup.
"""

import asyncio
import contextlib
import logging
import os
import traceback
from typing import List

from langchain_core.tools import BaseTool, StructuredTool
from langchain_mcp_adapters.client import MultiServerMCPClient
import langchain_mcp_adapters.sessions as _mcp_sessions
from mcp.client.stdio import stdio_client as _orig_stdio_client

from utils.user_config import get_mcp_servers
from resources.ui_strings import AgentStrings as S

logger = logging.getLogger(__name__)


@contextlib.asynccontextmanager
async def _quiet_stdio_client(server, **_kwargs):
    """Wrap stdio_client to suppress MCP server startup banners (sent to stderr).

    Uses os.devnull (a real file with fileno()) — required on Windows since
    subprocess creation calls msvcrt.get_osfhandle(errlog.fileno()).
    """
    with open(os.devnull, "w") as devnull:
        async with _orig_stdio_client(server, errlog=devnull) as result:
            yield result


# Patch langchain-mcp-adapters to use the quiet client
_mcp_sessions.stdio_client = _quiet_stdio_client

# MCP config keys that are DeskGenie-specific and must be stripped before
# passing configs to MultiServerMCPClient.
_DESKGENIE_KEYS = {"tools"}


def _build_server_configs() -> dict:
    """Build server configs for MultiServerMCPClient.

    - Injects full os.environ into stdio server configs (MCP SDK's
      get_default_environment() filters env vars and drops custom ones
      like HOMEASSISTANT_URL).
    - Strips DeskGenie-specific keys (e.g. "tools") not recognized by the library.
    - Merges any ``env`` block from the server config on top of os.environ so
      that secrets stored in config.json (e.g. HOMEASSISTANT_TOKEN) are passed
      through even when they are not set as system environment variables.
    """
    servers = {}
    for name, cfg in get_mcp_servers().items():
        cfg = {k: v for k, v in cfg.items() if k not in _DESKGENIE_KEYS}
        if cfg.get("transport") == "stdio":
            custom_env = cfg.get("env", {})
            cfg = {**cfg, "env": {**os.environ, **custom_env}}
        servers[name] = cfg
    return servers


def _friendly_server_name(server_key: str) -> str:
    """Convert a config key like 'home_assistant' to 'Home Assistant'."""
    return server_key.replace('_', ' ').title()


def _add_sync_wrapper(async_tool: BaseTool, server_key: str) -> StructuredTool:
    """Wrap an async-only MCP tool to support sync invocation and UI log emission."""
    from utils.log_streamer import get_global_logger
    display = S.MCP_TOOL_CALLED.format(
        server=_friendly_server_name(server_key),
        tool=async_tool.name,
    )

    async def arun(**kwargs):
        return await async_tool.ainvoke(kwargs)

    def run(**kwargs):
        get_global_logger().tool_call(display)
        return asyncio.run(arun(**kwargs))

    if async_tool.args_schema is not None:
        return StructuredTool(
            name=async_tool.name,
            description=async_tool.description,
            args_schema=async_tool.args_schema,
            func=run,
            coroutine=arun,
        )
    return StructuredTool(
        name=async_tool.name,
        description=async_tool.description,
        func=run,
        coroutine=arun,
    )


async def _load_tools_async() -> List:
    """Async helper that connects to each MCP server independently and retrieves tools.

    Filters per-server so a whitelist on one server does not affect tools
    from other servers.
    """
    server_configs = _build_server_configs()
    if not server_configs:
        return []

    all_tools: List = []
    mcp_servers_cfg = get_mcp_servers()

    for server_key, cfg in server_configs.items():
        try:
            client = MultiServerMCPClient({server_key: cfg})
            server_tools = await client.get_tools()

            # Apply this server's whitelist if one is configured
            whitelist = mcp_servers_cfg.get(server_key, {}).get("tools")
            if whitelist is not None:
                whitelist_set = set(whitelist)
                server_tools = [t for t in server_tools if t.name in whitelist_set]

            for t in server_tools:
                all_tools.append(_add_sync_wrapper(t, server_key))

        except Exception as e:
            logger.warning(S.MCP_TOOLS_FAILED.format(error=f"{server_key}: {e}"))
            logger.warning(traceback.format_exc())

    logger.info(S.MCP_TOOLS_LOADED.format(count=len(all_tools), servers=len(server_configs)))
    return all_tools


def _log_error(e: Exception) -> None:
    """Log exception with full traceback to expose sub-exceptions."""
    logger.warning(S.MCP_TOOLS_FAILED.format(error=e))
    logger.warning(traceback.format_exc())


def get_mcp_tools_list() -> List:
    """Load LangChain-compatible tools from all configured MCP servers.

    Returns:
        List of LangChain tools auto-discovered from MCP servers.
        Returns empty list if no servers configured or if loading fails.
    """
    if not get_mcp_servers():
        logger.debug(S.MCP_TOOLS_NONE_CONFIGURED)
        return []

    try:
        return asyncio.run(_load_tools_async())
    except RuntimeError:
        # Already inside a running event loop (e.g. FastAPI) — use a thread
        import concurrent.futures
        try:
            with concurrent.futures.ThreadPoolExecutor() as pool:
                return pool.submit(asyncio.run, _load_tools_async()).result()
        except Exception as e:
            _log_error(e)
            return []
    except Exception as e:
        _log_error(e)
        return []
