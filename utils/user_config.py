"""User configuration management for Desktop AI Agent.

Handles user preferences and folder aliases stored in a JSON config file.
Config is stored in the application data directory.
"""

import json
from pathlib import Path
from typing import Optional, Any

from utils.data_dir import get_config_path


# Default configuration structure
DEFAULT_CONFIG = {
    "folder_aliases": {},
    "preferences": {
        "default_output_dir": "downloads",
        "image_quality": 85,
        "pdf_dpi": 200,
    }
}


def _load_config() -> dict:
    """Load configuration from disk.

    Returns:
        Configuration dictionary, or default config if file doesn't exist
    """
    from resources.log_strings import ConfigMessages as CM

    config_path = get_config_path()

    if not config_path.exists():
        return DEFAULT_CONFIG.copy()

    try:
        with open(config_path, "r", encoding="utf-8") as f:
            config = json.load(f)
            # Merge with defaults to ensure all keys exist
            merged = DEFAULT_CONFIG.copy()
            merged["folder_aliases"] = {**merged.get("folder_aliases", {}),
                                         **config.get("folder_aliases", {})}
            merged["preferences"] = {**merged.get("preferences", {}),
                                      **config.get("preferences", {})}
            return merged
    except json.JSONDecodeError as e:
        print(CM.CONFIG_PARSE_ERROR.format(error=str(e)))
        print(CM.CONFIG_PATH_INFO.format(path=config_path))
        return DEFAULT_CONFIG.copy()
    except IOError as e:
        print(CM.CONFIG_READ_ERROR.format(error=str(e)))
        print(CM.CONFIG_PATH_INFO.format(path=config_path))
        return DEFAULT_CONFIG.copy()


def _save_config(config: dict) -> bool:
    """Save configuration to disk.

    Args:
        config: Configuration dictionary to save

    Returns:
        True if saved successfully, False otherwise
    """
    config_path = get_config_path()

    try:
        # Ensure parent directory exists
        config_path.parent.mkdir(parents=True, exist_ok=True)

        with open(config_path, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
        return True
    except IOError:
        return False


# --- Folder Aliases ---

def get_folder_alias(alias: str) -> Optional[str]:
    """Get the path for a folder alias.

    Args:
        alias: The alias name (case-insensitive)

    Returns:
        The path string or None if alias not found
    """
    config = _load_config()
    aliases = config.get("folder_aliases", {})

    # Case-insensitive lookup
    alias_lower = alias.lower()
    for key, value in aliases.items():
        if key.lower() == alias_lower:
            return value
    return None


def set_folder_alias(alias: str, path: str) -> bool:
    """Set a folder alias.

    Args:
        alias: The alias name
        path: The path to associate with the alias

    Returns:
        True if saved successfully
    """
    config = _load_config()

    if "folder_aliases" not in config:
        config["folder_aliases"] = {}

    config["folder_aliases"][alias.lower()] = path
    return _save_config(config)


def remove_folder_alias(alias: str) -> bool:
    """Remove a folder alias.

    Args:
        alias: The alias name to remove

    Returns:
        True if removed and saved, False if alias didn't exist
    """
    config = _load_config()
    aliases = config.get("folder_aliases", {})

    # Case-insensitive lookup
    alias_lower = alias.lower()
    key_to_remove = None
    for key in aliases:
        if key.lower() == alias_lower:
            key_to_remove = key
            break

    if key_to_remove is None:
        return False

    del config["folder_aliases"][key_to_remove]
    return _save_config(config)


def list_folder_aliases() -> dict[str, str]:
    """Get all folder aliases.

    Returns:
        Dictionary of alias -> path mappings
    """
    config = _load_config()
    return config.get("folder_aliases", {})


# --- Preferences ---

def get_preference(key: str, default: Any = None) -> Any:
    """Get a preference value.

    Args:
        key: The preference key
        default: Default value if key not found

    Returns:
        The preference value or default
    """
    config = _load_config()
    return config.get("preferences", {}).get(key, default)


def set_preference(key: str, value: Any) -> bool:
    """Set a preference value.

    Args:
        key: The preference key
        value: The value to set

    Returns:
        True if saved successfully
    """
    config = _load_config()

    if "preferences" not in config:
        config["preferences"] = {}

    config["preferences"][key] = value
    return _save_config(config)


def get_all_preferences() -> dict:
    """Get all preferences.

    Returns:
        Dictionary of all preferences
    """
    config = _load_config()
    return config.get("preferences", {})


# --- Full Config ---

def get_full_config() -> dict:
    """Get the full configuration.

    Returns:
        Complete configuration dictionary
    """
    return _load_config()


def reset_config() -> bool:
    """Reset configuration to defaults.

    Returns:
        True if saved successfully
    """
    return _save_config(DEFAULT_CONFIG.copy())
