"""Shared ChromaDB persistent client — singleton per process."""

import threading
from typing import Optional

from utils.data_dir import get_memory_dir

_lock = threading.Lock()
_client = None
_collection = None


def get_episodic_collection():
    """Return the ChromaDB episodic collection, initializing on first call.

    Returns:
        ChromaDB Collection object with cosine distance space.

    Raises:
        Exception: If ChromaDB cannot be initialized (caller should catch and degrade).
    """
    global _client, _collection

    if _collection is not None:
        return _collection

    with _lock:
        if _collection is not None:
            return _collection

        import chromadb

        chroma_dir = get_memory_dir() / "chroma"
        _client = chromadb.PersistentClient(path=str(chroma_dir))
        _collection = _client.get_or_create_collection(
            name="episodic",
            metadata={"hnsw:space": "cosine"}
        )

    return _collection
