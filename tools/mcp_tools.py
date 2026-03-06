"""MCP (Model Context Protocol) tool loader.

Loads LangChain-compatible tools from all configured MCP servers defined in config.MCP_SERVERS.
Adding a new MCP server requires only a single config entry — tools are auto-discovered.
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

from app import config
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
    """
    servers = {}
    for name, cfg in config.MCP_SERVERS.items():
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
    for cfg in config.MCP_SERVERS.values():
        if "tools" in cfg:
            whitelisted.update(cfg["tools"])
    return whitelisted


def _add_sync_wrapper(async_tool: StructuredTool) -> StructuredTool:
    """Wrap an async-only MCP tool to support sync invocation via asyncio.run()."""
    async def arun(**kwargs):
        return await async_tool.ainvoke(kwargs)

    def run(**kwargs):
        return asyncio.run(arun(**kwargs))

    return StructuredTool(
        name=async_tool.name,
        description=async_tool.description,
        args_schema=async_tool.args_schema,
        func=run,
        coroutine=arun,
    )


async def _load_tools_async() -> List:
    """Async helper that connects to all configured MCP servers and retrieves their tools."""
    if not config.MCP_SERVERS:
        return []
    client = MultiServerMCPClient(_build_server_configs())
    raw_tools = await client.get_tools()

    whitelist = _build_tool_whitelist()
    if whitelist:
        raw_tools = [t for t in raw_tools if t.name in whitelist]

    tools = [_add_sync_wrapper(t) for t in raw_tools]
    logger.info(S.MCP_TOOLS_LOADED.format(count=len(tools), servers=len(config.MCP_SERVERS)))
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
    if not config.MCP_SERVERS:
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
