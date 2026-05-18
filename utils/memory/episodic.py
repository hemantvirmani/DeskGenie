"""Episodic memory — index and retrieve past Q&A episodes via ChromaDB."""

from typing import Optional
from resources.log_strings import MemoryMessages as MM


def index_episode(
    chat_id: str,
    chat_name: str,
    msg_index: int,
    question: str,
    answer: str,
    tools_used: Optional[list] = None,
    has_file: bool = False,
) -> None:
    """Store a Q&A episode in the ChromaDB episodic collection.

    Args:
        chat_id: Chat group ID (used as part of the document ID).
        chat_name: Human-readable chat name (displayed in retrieved context).
        msg_index: Message index within the chat (makes the ID unique per turn).
        question: The user's question.
        answer: The agent's answer.
        tools_used: List of tool names used during the run.
        has_file: Whether the question referenced a file.
    """
    from utils.memory.chroma_client import get_episodic_collection

    try:
        collection = get_episodic_collection()
        doc_id = f"{chat_id}_msg_{msg_index}"
        text = f"Q: {question}\nA: {answer}"
        metadata = {
            "chat_id": chat_id,
            "chat_name": chat_name,
            "msg_index": msg_index,
            "has_file": has_file,
            "tools_used": ",".join(tools_used or []),
        }
        collection.upsert(ids=[doc_id], documents=[text], metadatas=[metadata])
        print(MM.EPISODIC_INDEXED.format(doc_id=doc_id))
    except Exception as e:
        print(MM.EPISODIC_INDEX_ERROR.format(error=e))


def retrieve_similar_episodes(
    question: str,
    exclude_chat_id: Optional[str] = None,
    top_k: int = 3,
    threshold: float = 0.72,
) -> list:
    """Retrieve episodes from the past that are semantically similar to the question.

    Excludes episodes from the current chat session (already covered by short-term history).
    Only returns results above the similarity threshold.

    Args:
        question: The current question to match against.
        exclude_chat_id: Chat ID whose episodes are excluded.
        top_k: Maximum number of episodes to return.
        threshold: Minimum cosine similarity (0–1) for an episode to be included.

    Returns:
        List of dicts: [{text, metadata, similarity}], ordered by similarity descending.
        Empty list on any failure (graceful degradation).
    """
    from utils.memory.chroma_client import get_episodic_collection

    try:
        collection = get_episodic_collection()
        count = collection.count()
        if count == 0:
            return []

        # Query more than top_k so we have room to filter by threshold and chat_id
        n_results = min(top_k * 3, count)
        results = collection.query(
            query_texts=[question],
            n_results=n_results,
            include=["documents", "metadatas", "distances"],
        )

        docs = results.get("documents", [[]])[0]
        metas = results.get("metadatas", [[]])[0]
        dists = results.get("distances", [[]])[0]

        episodes = []
        for doc, meta, dist in zip(docs, metas, dists):
            # ChromaDB cosine space: distance = 1 - cosine_similarity (for normalized embeddings)
            similarity = 1.0 - dist
            if similarity < threshold:
                continue
            if exclude_chat_id and meta.get("chat_id") == exclude_chat_id:
                continue
            episodes.append({"text": doc, "metadata": meta, "similarity": similarity})

        return episodes[:top_k]

    except Exception as e:
        print(MM.EPISODIC_QUERY_ERROR.format(error=e))
        return []
