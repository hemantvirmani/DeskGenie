"""MemoryManager — orchestrates episodic context retrieval and post-run indexing."""

from typing import Optional

from utils.user_config import get_memory_config
from resources.log_strings import MemoryMessages as MM


# Responses that carry no useful information and should never be indexed
_SKIP_PATTERNS = (
    "Error:",
    "I reached my maximum",
    "No answer",
    "I don't have access to that information",
    "I don't know your",
    "I don't have any information",
)


class MemoryManager:
    """Manages episodic memory: retrieves context before a run, indexes after."""

    def build_context(self, question: str, chat_id: Optional[str]) -> str:
        """Retrieve formatted episodic context for injection into the system prompt.

        Args:
            question: The current user question.
            chat_id: Current chat group ID (episodes from this chat are excluded).

        Returns:
            Formatted string block of relevant past Q&A pairs, or empty string if
            memory is disabled, no results meet the threshold, or retrieval fails.
        """
        cfg = get_memory_config()
        if not cfg.get("enabled", True):
            return ""
        episodic_cfg = cfg.get("episodic", {})
        if not episodic_cfg.get("enabled", True):
            return ""

        top_k = episodic_cfg.get("topK", 3)
        threshold = episodic_cfg.get("similarityThreshold", 0.72)

        from utils.memory.episodic import retrieve_similar_episodes

        episodes = retrieve_similar_episodes(
            question=question,
            exclude_chat_id=chat_id,
            top_k=top_k,
            threshold=threshold,
        )

        if not episodes:
            return ""

        lines = []
        for ep in episodes:
            meta = ep["metadata"]
            chat_name = meta.get("chat_name", "Past chat")
            lines.append(f"[{chat_name}]")
            lines.append(ep["text"])
            lines.append("")

        return "\n".join(lines).rstrip()

    def post_run_index(
        self,
        chat_id: str,
        chat_name: str,
        msg_index: int,
        question: str,
        answer: str,
        has_file: bool = False,
    ) -> None:
        """Index a completed Q&A episode for future episodic retrieval.

        Skips indexing if memory is disabled, the answer signals an error,
        or the episode is from CLI mode (no chat_id).

        Args:
            chat_id: Chat group ID.
            chat_name: Human-readable chat name.
            msg_index: Message position in the chat (used for unique doc ID).
            question: The user's question.
            answer: The agent's answer.
            has_file: Whether the question referenced a file.
        """
        if not chat_id:
            return

        cfg = get_memory_config()
        if not cfg.get("enabled", True):
            return
        if not cfg.get("episodic", {}).get("enabled", True):
            print(MM.EPISODIC_SKIPPED_DISABLED)
            return

        if not answer.strip() or any(answer.startswith(p) for p in _SKIP_PATTERNS):
            print(MM.EPISODIC_SKIPPED_ERROR)
            return

        from utils.memory.episodic import index_episode

        index_episode(
            chat_id=chat_id,
            chat_name=chat_name,
            msg_index=msg_index,
            question=question,
            answer=answer,
            has_file=has_file,
        )
