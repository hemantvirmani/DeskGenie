"""User configuration management for Desktop AI Agent.

Handles user preferences, folder aliases, LLM settings, MCP servers, and log
level — all stored in a single config.json file.

Load order (first found wins):
  1. Platform app-data dir  — %LOCALAPPDATA%\\DeskGenie\\config.json  (Windows)
                               ~/Library/Application Support/DeskGenie/config.json  (macOS)
                               ~/.local/share/DeskGenie/config.json  (Linux)
  2. Fallback directory     — directory of the running exe / current working directory

A console message is printed when the fallback path is used or when the file
cannot be found at all.
"""

import json
import logging
import sys
from pathlib import Path
from typing import Optional, Any

from utils.data_dir import get_config_path

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Valid log-level names recognised by Python's logging module
# ---------------------------------------------------------------------------
_VALID_LOG_LEVELS = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}

# ---------------------------------------------------------------------------
# Default configuration — all sections with sensible built-in values.
# Users should copy config.json.example and fill in their API keys.
# ---------------------------------------------------------------------------
DEFAULT_CONFIG: dict = {
    # ------------------------------------------------------------------
    # LLM configuration
    # ------------------------------------------------------------------
    "llm": {
        # Which provider to use for the main agent loop.
        # One of: "google" | "anthropic" | "ollama" | "huggingface"
        "activeProvider": "google",

        # Temperature applied to the agent LLM (all providers).
        "agentTemperature": 0.0,

        # Seconds to wait for a single LLM API call before timing out.
        "callTimeout": 300,

        "providers": {
            "google": {
                # Get your key at https://aistudio.google.com
                "apiKey": "",
                # Main agent model
                "agentModel": "gemini-2.5-flash",
                # Model used by vision / analysis tools
                "visionModel": "gemini-2.5-flash",
                # Advisor tool uses a more capable model for hard reasoning
                "advisorModel": "gemini-3.1-pro-preview",
                # Temperature for vision/analysis calls (keep 0 for determinism)
                "visionTemperature": 0,
                # Max tokens returned by vision/analysis calls
                "maxOutputTokens": 1024
            },
            "anthropic": {
                # Get your key at https://console.anthropic.com
                "apiKey": "",
                "model": "claude-sonnet-4-5-20250929"
            },
            "ollama": {
                # URL of the Ollama server (local or remote)
                "baseUrl": "http://127.0.0.1:11434",
                "model": "qwen3.5:2b"
            },
            "huggingface": {
                # Get your token at https://huggingface.co/settings/tokens
                "apiKey": "",
                "model": "meta-llama/Llama-3.1-8B-Instruct"
            }
        }
    },

    # ------------------------------------------------------------------
    # MCP server configuration (same structure as Claude Code settings.json)
    # Each key is a server name; supported transports: "stdio" | "sse"
    # ------------------------------------------------------------------
    "mcpServers": {},

    # ------------------------------------------------------------------
    # Logging
    # ------------------------------------------------------------------
    "logging": {
        # Python log level: DEBUG | INFO | WARNING | ERROR | CRITICAL
        "level": "INFO"
    },

    # ------------------------------------------------------------------
    # Folder aliases — short names that resolve to real paths.
    # Example: "prax" -> "C:/Work/Praxis"
    # ------------------------------------------------------------------
    "folder_aliases": {},

    # ------------------------------------------------------------------
    # Tool behaviour preferences
    # ------------------------------------------------------------------
    "preferences": {
        "default_output_dir": "downloads",
        "image_quality": 85,
        "pdf_dpi": 200
    }
}


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _get_fallback_dir() -> Path:
    """Return the directory of the running exe or, in dev mode, the cwd."""
    if getattr(sys, "frozen", False):
        # PyInstaller bundle — use the folder containing the exe
        return Path(sys.executable).parent
    return Path.cwd()


def _deep_merge(base: dict, override: dict) -> dict:
    """Recursively merge *override* into a copy of *base*.

    Nested dicts are merged rather than replaced so that a partial
    config.json still picks up all default values for missing keys.
    """
    result = base.copy()
    for key, value in override.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = _deep_merge(result[key], value)
        else:
            result[key] = value
    return result


def _try_load_json(path: Path) -> Optional[dict]:
    """Attempt to parse a JSON file; return None on any error."""
    from resources.log_strings import ConfigMessages as CM
    try:
        with open(path, "r", encoding="utf-8") as fh:
            return json.load(fh)
    except json.JSONDecodeError as exc:
        print(CM.CONFIG_PARSE_ERROR.format(error=exc))
        print(CM.CONFIG_PATH_INFO.format(path=path))
        return None
    except IOError as exc:
        print(CM.CONFIG_READ_ERROR.format(error=exc))
        print(CM.CONFIG_PATH_INFO.format(path=path))
        return None


def _load_config() -> dict:
    """Load config.json with two-path fallback.

    Returns:
        Merged configuration dict (user values overlaid on DEFAULT_CONFIG).
    """
    from resources.log_strings import ConfigMessages as CM

    default_path: Path = get_config_path()
    fallback_path: Path = _get_fallback_dir() / "config.json"

    raw: Optional[dict] = None

    if default_path.exists():
        raw = _try_load_json(default_path)
    else:
        # Only print the fallback notice when the fallback path is *different*
        if default_path != fallback_path:
            print(CM.CONFIG_NOT_FOUND_DEFAULT.format(
                path=default_path, fallback=fallback_path
            ))

        if fallback_path.exists():
            raw = _try_load_json(fallback_path)
            if raw is not None:
                print(CM.CONFIG_LOADED_FALLBACK.format(path=fallback_path))
        else:
            print(CM.CONFIG_NOT_FOUND_ANYWHERE.format(
                default=default_path, fallback=fallback_path
            ))

    if raw is None:
        return _deep_merge({}, DEFAULT_CONFIG)

    return _deep_merge(DEFAULT_CONFIG, raw)


def _save_config(config: dict) -> bool:
    """Persist *config* to the default app-data path.

    Returns:
        True on success, False otherwise.
    """
    config_path = get_config_path()
    try:
        config_path.parent.mkdir(parents=True, exist_ok=True)
        with open(config_path, "w", encoding="utf-8") as fh:
            json.dump(config, fh, indent=2, ensure_ascii=False)
        return True
    except IOError:
        return False


# ---------------------------------------------------------------------------
# Public read helpers
# ---------------------------------------------------------------------------

def get_llm_config() -> dict:
    """Return the full ``llm`` section of config.json.

    Returns:
        Dict with keys ``activeProvider``, ``agentTemperature``,
        ``callTimeout``, and ``providers``.
    """
    return _load_config().get("llm", DEFAULT_CONFIG["llm"])


def get_active_provider() -> str:
    """Return the active LLM provider name (e.g. ``"google"``).

    Returns:
        Provider string; falls back to ``"google"`` if unrecognised.
    """
    from resources.log_strings import ConfigMessages as CM
    from resources.state_strings import ModelProviders as MP

    provider = get_llm_config().get("activeProvider", "google")
    valid = {MP.GOOGLE, MP.ANTHROPIC, MP.OLLAMA, MP.HUGGINGFACE}
    if provider not in valid:
        print(CM.LLM_UNKNOWN_PROVIDER.format(provider=provider))
        return MP.GOOGLE
    return provider


def get_provider_config(provider: str) -> dict:
    """Return the configuration sub-dict for a specific provider.

    Args:
        provider: One of ``"google"``, ``"anthropic"``, ``"ollama"``,
                  ``"huggingface"``.

    Returns:
        Provider config dict merged with defaults.
    """
    providers = get_llm_config().get("providers", {})
    defaults = DEFAULT_CONFIG["llm"]["providers"].get(provider, {})
    return _deep_merge(defaults, providers.get(provider, {}))


def get_mcp_servers() -> dict:
    """Return the ``mcpServers`` section of config.json.

    Returns:
        Dict mapping server name → transport config (same shape as
        Claude Code's settings.json ``mcpServers`` block).
    """
    return _load_config().get("mcpServers", {})


def get_log_level() -> int:
    """Return the Python ``logging`` level integer from config.json.

    Returns:
        A ``logging.*`` constant (e.g. ``logging.INFO``). Defaults to
        ``logging.INFO`` for invalid/missing values.
    """
    from resources.log_strings import ConfigMessages as CM

    level_str: str = _load_config().get("logging", {}).get("level", "INFO").upper()
    if level_str not in _VALID_LOG_LEVELS:
        print(CM.LOG_LEVEL_INVALID.format(level=level_str))
        return logging.INFO
    return getattr(logging, level_str)


# ---------------------------------------------------------------------------
# Folder aliases (read/write)
# ---------------------------------------------------------------------------

def get_folder_alias(alias: str) -> Optional[str]:
    """Get the path for a folder alias.

    Args:
        alias: The alias name (case-insensitive).

    Returns:
        The path string or None if alias not found.
    """
    config = _load_config()
    aliases = config.get("folder_aliases", {})
    alias_lower = alias.lower()
    for key, value in aliases.items():
        if key.lower() == alias_lower:
            return value
    return None


def set_folder_alias(alias: str, path: str) -> bool:
    """Set a folder alias.

    Args:
        alias: The alias name.
        path: The path to associate with the alias.

    Returns:
        True if saved successfully.
    """
    config = _load_config()
    config.setdefault("folder_aliases", {})[alias.lower()] = path
    return _save_config(config)


def remove_folder_alias(alias: str) -> bool:
    """Remove a folder alias.

    Args:
        alias: The alias name to remove.

    Returns:
        True if removed and saved, False if alias didn't exist.
    """
    config = _load_config()
    aliases = config.get("folder_aliases", {})
    alias_lower = alias.lower()
    key_to_remove = next((k for k in aliases if k.lower() == alias_lower), None)
    if key_to_remove is None:
        return False
    del config["folder_aliases"][key_to_remove]
    return _save_config(config)


def list_folder_aliases() -> dict[str, str]:
    """Get all folder aliases.

    Returns:
        Dictionary of alias -> path mappings.
    """
    return _load_config().get("folder_aliases", {})


# ---------------------------------------------------------------------------
# Preferences (read/write)
# ---------------------------------------------------------------------------

def get_preference(key: str, default: Any = None) -> Any:
    """Get a preference value.

    Args:
        key: The preference key.
        default: Default value if key not found.

    Returns:
        The preference value or default.
    """
    return _load_config().get("preferences", {}).get(key, default)


def set_preference(key: str, value: Any) -> bool:
    """Set a preference value.

    Args:
        key: The preference key.
        value: The value to set.

    Returns:
        True if saved successfully.
    """
    config = _load_config()
    config.setdefault("preferences", {})[key] = value
    return _save_config(config)


def get_all_preferences() -> dict:
    """Get all preferences.

    Returns:
        Dictionary of all preferences.
    """
    return _load_config().get("preferences", {})


# ---------------------------------------------------------------------------
# Full config access / reset
# ---------------------------------------------------------------------------

def get_full_config() -> dict:
    """Get the full merged configuration.

    Returns:
        Complete configuration dictionary.
    """
    return _load_config()


def reset_config() -> bool:
    """Reset configuration to defaults.

    Returns:
        True if saved successfully.
    """
    import copy
    return _save_config(copy.deepcopy(DEFAULT_CONFIG))
