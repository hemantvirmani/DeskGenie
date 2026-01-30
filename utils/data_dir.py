"""Utility for managing application and system directories.

Provides cross-platform support for accessing:
- Application data directories
- Standard user directories (Documents, Downloads, Desktop, etc.)
- System directories
"""

import os
import platform
from pathlib import Path
from typing import Optional

APP_NAME = "DeskGenie"


# --- Application Data Directories ---

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


# --- Standard User Directories ---

def get_home_dir() -> Path:
    """Get the user's home directory.

    Returns:
        Path to home directory
    """
    return Path.home()


def get_documents_dir() -> Path:
    """Get the user's Documents directory.

    Returns:
        Path to Documents directory
    """
    system = platform.system()

    if system == "Windows":
        # Try to get from environment or use default
        docs = os.environ.get("USERPROFILE", "")
        if docs:
            return Path(docs) / "Documents"
        return Path.home() / "Documents"
    elif system == "Darwin":
        return Path.home() / "Documents"
    else:  # Linux
        # Check XDG user dirs
        xdg_docs = os.environ.get("XDG_DOCUMENTS_DIR")
        if xdg_docs:
            return Path(xdg_docs)
        return Path.home() / "Documents"


def get_downloads_dir() -> Path:
    """Get the user's Downloads directory.

    Returns:
        Path to Downloads directory
    """
    system = platform.system()

    if system == "Windows":
        userprofile = os.environ.get("USERPROFILE", "")
        if userprofile:
            return Path(userprofile) / "Downloads"
        return Path.home() / "Downloads"
    elif system == "Darwin":
        return Path.home() / "Downloads"
    else:  # Linux
        xdg_downloads = os.environ.get("XDG_DOWNLOAD_DIR")
        if xdg_downloads:
            return Path(xdg_downloads)
        return Path.home() / "Downloads"


def get_desktop_dir() -> Path:
    """Get the user's Desktop directory.

    Returns:
        Path to Desktop directory
    """
    system = platform.system()

    if system == "Windows":
        userprofile = os.environ.get("USERPROFILE", "")
        if userprofile:
            return Path(userprofile) / "Desktop"
        return Path.home() / "Desktop"
    elif system == "Darwin":
        return Path.home() / "Desktop"
    else:  # Linux
        xdg_desktop = os.environ.get("XDG_DESKTOP_DIR")
        if xdg_desktop:
            return Path(xdg_desktop)
        return Path.home() / "Desktop"


def get_pictures_dir() -> Path:
    """Get the user's Pictures directory.

    Returns:
        Path to Pictures directory
    """
    system = platform.system()

    if system == "Windows":
        userprofile = os.environ.get("USERPROFILE", "")
        if userprofile:
            return Path(userprofile) / "Pictures"
        return Path.home() / "Pictures"
    elif system == "Darwin":
        return Path.home() / "Pictures"
    else:  # Linux
        xdg_pictures = os.environ.get("XDG_PICTURES_DIR")
        if xdg_pictures:
            return Path(xdg_pictures)
        return Path.home() / "Pictures"


def get_videos_dir() -> Path:
    """Get the user's Videos directory.

    Returns:
        Path to Videos directory
    """
    system = platform.system()

    if system == "Windows":
        userprofile = os.environ.get("USERPROFILE", "")
        if userprofile:
            return Path(userprofile) / "Videos"
        return Path.home() / "Videos"
    elif system == "Darwin":
        return Path.home() / "Movies"
    else:  # Linux
        xdg_videos = os.environ.get("XDG_VIDEOS_DIR")
        if xdg_videos:
            return Path(xdg_videos)
        return Path.home() / "Videos"


def get_music_dir() -> Path:
    """Get the user's Music directory.

    Returns:
        Path to Music directory
    """
    system = platform.system()

    if system == "Windows":
        userprofile = os.environ.get("USERPROFILE", "")
        if userprofile:
            return Path(userprofile) / "Music"
        return Path.home() / "Music"
    elif system == "Darwin":
        return Path.home() / "Music"
    else:  # Linux
        xdg_music = os.environ.get("XDG_MUSIC_DIR")
        if xdg_music:
            return Path(xdg_music)
        return Path.home() / "Music"


# --- System/Application Directories ---

def get_local_appdata_dir() -> Path:
    """Get the Local Application Data directory.

    Returns:
        Path to Local AppData (Windows) or equivalent
    """
    system = platform.system()

    if system == "Windows":
        return Path(os.environ.get("LOCALAPPDATA", Path.home() / "AppData" / "Local"))
    elif system == "Darwin":
        return Path.home() / "Library" / "Application Support"
    else:  # Linux
        return Path(os.environ.get("XDG_DATA_HOME", Path.home() / ".local" / "share"))


def get_roaming_appdata_dir() -> Path:
    """Get the Roaming Application Data directory.

    Returns:
        Path to Roaming AppData (Windows) or equivalent
    """
    system = platform.system()

    if system == "Windows":
        return Path(os.environ.get("APPDATA", Path.home() / "AppData" / "Roaming"))
    elif system == "Darwin":
        return Path.home() / "Library" / "Application Support"
    else:  # Linux
        return Path(os.environ.get("XDG_CONFIG_HOME", Path.home() / ".config"))


def get_temp_dir() -> Path:
    """Get the system temporary directory.

    Returns:
        Path to temp directory
    """
    system = platform.system()

    if system == "Windows":
        return Path(os.environ.get("TEMP", os.environ.get("TMP", "C:\\Temp")))
    else:
        return Path(os.environ.get("TMPDIR", "/tmp"))


def get_program_files_dir() -> Optional[Path]:
    """Get the Program Files directory (Windows only).

    Returns:
        Path to Program Files or None if not Windows
    """
    if platform.system() != "Windows":
        return None

    return Path(os.environ.get("ProgramFiles", "C:\\Program Files"))


def get_program_files_x86_dir() -> Optional[Path]:
    """Get the Program Files (x86) directory (Windows only).

    Returns:
        Path to Program Files (x86) or None if not Windows/not available
    """
    if platform.system() != "Windows":
        return None

    x86 = os.environ.get("ProgramFiles(x86)")
    if x86:
        return Path(x86)
    return None


# --- Utility Functions ---

def get_all_user_dirs() -> dict[str, Path]:
    """Get all standard user directories as a dictionary.

    Returns:
        Dictionary mapping directory names to their paths
    """
    return {
        "home": get_home_dir(),
        "documents": get_documents_dir(),
        "downloads": get_downloads_dir(),
        "desktop": get_desktop_dir(),
        "pictures": get_pictures_dir(),
        "videos": get_videos_dir(),
        "music": get_music_dir(),
    }


def get_all_system_dirs() -> dict[str, Optional[Path]]:
    """Get all system/application directories as a dictionary.

    Returns:
        Dictionary mapping directory names to their paths
    """
    return {
        "local_appdata": get_local_appdata_dir(),
        "roaming_appdata": get_roaming_appdata_dir(),
        "temp": get_temp_dir(),
        "program_files": get_program_files_dir(),
        "program_files_x86": get_program_files_x86_dir(),
    }


def resolve_path_alias(alias: str) -> Optional[Path]:
    """Resolve a path alias to an actual path.

    Supports aliases like:
    - ~, home, $HOME -> Home directory
    - documents, docs -> Documents
    - downloads -> Downloads
    - desktop -> Desktop
    - pictures, photos -> Pictures
    - videos, movies -> Videos
    - music -> Music
    - appdata, localappdata -> Local AppData
    - roaming -> Roaming AppData
    - temp, tmp -> Temp directory

    Args:
        alias: The alias to resolve

    Returns:
        Resolved Path or None if alias not recognized
    """
    alias = alias.lower().strip()

    alias_map = {
        "~": get_home_dir,
        "home": get_home_dir,
        "$home": get_home_dir,
        "documents": get_documents_dir,
        "docs": get_documents_dir,
        "my documents": get_documents_dir,
        "downloads": get_downloads_dir,
        "desktop": get_desktop_dir,
        "pictures": get_pictures_dir,
        "photos": get_pictures_dir,
        "my pictures": get_pictures_dir,
        "videos": get_videos_dir,
        "movies": get_videos_dir,
        "my videos": get_videos_dir,
        "music": get_music_dir,
        "my music": get_music_dir,
        "appdata": get_local_appdata_dir,
        "localappdata": get_local_appdata_dir,
        "local appdata": get_local_appdata_dir,
        "roaming": get_roaming_appdata_dir,
        "roaming appdata": get_roaming_appdata_dir,
        "temp": get_temp_dir,
        "tmp": get_temp_dir,
    }

    if alias in alias_map:
        return alias_map[alias]()
    return None
