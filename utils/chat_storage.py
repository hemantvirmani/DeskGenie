"""Chat storage module for persisting chat groups to disk.

Stores each chat group as a separate JSON file in the chats directory.
"""

import json
from pathlib import Path
from typing import Optional

from utils.data_dir import get_chats_dir


def list_chats() -> list[dict]:
    """List all saved chat groups.

    Returns:
        List of chat group objects, sorted by updatedAt (newest first)
    """
    chats_dir = get_chats_dir()
    chats = []

    for chat_file in chats_dir.glob("*.json"):
        try:
            with open(chat_file, "r", encoding="utf-8") as f:
                chat = json.load(f)
                chats.append(chat)
        except (json.JSONDecodeError, IOError):
            continue

    # Sort by updatedAt, newest first
    chats.sort(key=lambda c: c.get("updatedAt", 0), reverse=True)
    return chats


def get_chat(chat_id: str) -> Optional[dict]:
    """Get a specific chat group by ID.

    Args:
        chat_id: The chat group ID

    Returns:
        Chat group object or None if not found
    """
    chat_path = get_chats_dir() / f"{chat_id}.json"

    if not chat_path.exists():
        return None

    try:
        with open(chat_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return None


def save_chat(chat: dict) -> bool:
    """Save a chat group to disk.

    Args:
        chat: Chat group object with at least an 'id' field

    Returns:
        True if saved successfully, False otherwise
    """
    if "id" not in chat:
        return False

    chat_path = get_chats_dir() / f"{chat['id']}.json"

    try:
        with open(chat_path, "w", encoding="utf-8") as f:
            json.dump(chat, f, indent=2, ensure_ascii=False)
        return True
    except IOError:
        return False


def delete_chat(chat_id: str) -> bool:
    """Delete a chat group from disk.

    Args:
        chat_id: The chat group ID

    Returns:
        True if deleted successfully, False otherwise
    """
    chat_path = get_chats_dir() / f"{chat_id}.json"

    if not chat_path.exists():
        return False

    try:
        chat_path.unlink()
        return True
    except IOError:
        return False


def save_all_chats(chats: list[dict]) -> bool:
    """Save multiple chat groups at once.

    Args:
        chats: List of chat group objects

    Returns:
        True if all saved successfully, False otherwise
    """
    success = True
    for chat in chats:
        if not save_chat(chat):
            success = False
    return success
