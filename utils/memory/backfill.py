"""One-time backfill script: indexes all existing chat JSON files into ChromaDB.

Run from the project root:
    python utils/memory/backfill.py
"""

import sys
from pathlib import Path

_project_root = Path(__file__).parent.parent.parent
if str(_project_root) not in sys.path:
    sys.path.insert(0, str(_project_root))

from utils.chat_storage import list_chats, get_chat
from utils.memory.episodic import index_episode
from resources.log_strings import MemoryMessages as MM


def backfill() -> None:
    """Index all historical chat Q&A pairs that have not yet been indexed."""
    chats = list_chats()
    total_indexed = 0

    for summary in chats:
        chat_id = summary.get("id", "")
        chat_name = summary.get("name", "Unknown")
        if not chat_id:
            continue

        chat = get_chat(chat_id)
        if not chat:
            continue

        messages = chat.get("messages", [])
        i = 0
        while i < len(messages) - 1:
            user_msg = messages[i]
            asst_msg = messages[i + 1]

            if (
                user_msg.get("role") == "user"
                and asst_msg.get("role") == "assistant"
                and asst_msg.get("status") not in ("loading", "interrupted", "error")
                and asst_msg.get("content", "").strip()
                and not any(
                    asst_msg["content"].startswith(p)
                    for p in ("Error:", "I reached my maximum", "No answer")
                )
            ):
                index_episode(
                    chat_id=chat_id,
                    chat_name=chat_name,
                    msg_index=i,
                    question=user_msg["content"],
                    answer=asst_msg["content"],
                )
                total_indexed += 1
                i += 2
            else:
                i += 1

    print(MM.BACKFILL_COMPLETE.format(total=total_indexed, chats=len(chats)))


if __name__ == "__main__":
    backfill()
