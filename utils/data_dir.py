"""Utility for managing application data directory.

Provides cross-platform support for storing user data in OS-standard locations:
- Windows: %LOCALAPPDATA%/DeskGenie/
- macOS: ~/Library/Application Support/DeskGenie/
- Linux: ~/.local/share/DeskGenie/
"""

import os
import platform
from pathlib import Path

APP_NAME = "DeskGenie"


def get_data_dir() -> Path:
    """Get the application data directory, creating it if necessary.

    Returns:
        Path to the data directory
    """
    system = platform.system()

    if system == "Windows":
        base = Path(os.environ.get("LOCALAPPDATA", Path.home() / "AppData" / "Local"))
    elif system == "Darwin":  # macOS
        base = Path.home() / "Library" / "Application Support"
    else:  # Linux and others
        base = Path(os.environ.get("XDG_DATA_HOME", Path.home() / ".local" / "share"))

    data_dir = base / APP_NAME
    data_dir.mkdir(parents=True, exist_ok=True)
    return data_dir


def get_chats_dir() -> Path:
    """Get the directory for storing chat data.

    Returns:
        Path to the chats directory
    """
    chats_dir = get_data_dir() / "chats"
    chats_dir.mkdir(parents=True, exist_ok=True)
    return chats_dir


def get_config_path() -> Path:
    """Get the path to the config file.

    Returns:
        Path to config.json
    """
    return get_data_dir() / "config.json"
