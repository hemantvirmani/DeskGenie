"""MCP (Model Context Protocol) tool loader.

Loads LangChain-compatible tools from all configured MCP servers defined in
the ``mcpServers`` section of config.json.
Adding a new MCP server requires only a single config.json entry — tools are
auto-discovered at startup.
"""

import asyncio
import contextlib
import io
import logging
import os
import traceback
from contextlib import redirect_stderr
from typing import List

from langchain_core.tools import StructuredTool
from langchain_mcp_adapters.client import MultiServerMCPClient
import langchain_mcp_adapters.sessions as _mcp_sessions
from mcp.client.stdio import stdio_client as _orig_stdio_client

from utils.user_config import get_mcp_servers
from resources.ui_strings import AgentStrings as S

logger = logging.getLogger(__name__)


@contextlib.asynccontextmanager
async def _quiet_stdio_client(server, errlog=None):
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


def _build_tool_whitelist() -> set:
    """Collect all whitelisted tool names across all servers.

    Returns an empty set if no server specifies a whitelist (meaning include all).
    """
    whitelisted: set = set()
    for cfg in get_mcp_servers().values():
        if "tools" in cfg:
            whitelisted.update(cfg["tools"])
    return whitelisted


def _friendly_server_name(server_key: str) -> str:
    """Convert a config key like 'home_assistant' to 'Home Assistant'."""
    return server_key.replace('_', ' ').title()


def _add_sync_wrapper(async_tool: StructuredTool, server_key: str) -> StructuredTool:
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

    return StructuredTool(
        name=async_tool.name,
        description=async_tool.description,
        args_schema=async_tool.args_schema,
        func=run,
        coroutine=arun,
    )


def _build_tool_to_server_map() -> dict:
    """Map each whitelisted tool name to its server key for log display."""
    mapping = {}
    for server_key, cfg in get_mcp_servers().items():
        for tool_name in cfg.get('tools', []):
            mapping[tool_name] = server_key
    return mapping


async def _load_tools_async() -> List:
    """Async helper that connects to all configured MCP servers and retrieves their tools."""
    mcp_servers = get_mcp_servers()
    if not mcp_servers:
        return []
    client = MultiServerMCPClient(_build_server_configs())
    raw_tools = await client.get_tools()

    whitelist = _build_tool_whitelist()
    if whitelist:
        raw_tools = [t for t in raw_tools if t.name in whitelist]

    tool_to_server = _build_tool_to_server_map()
    tools = [
        _add_sync_wrapper(t, tool_to_server.get(t.name, 'mcp'))
        for t in raw_tools
    ]
    logger.info(S.MCP_TOOLS_LOADED.format(count=len(tools), servers=len(mcp_servers)))
    return tools


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
