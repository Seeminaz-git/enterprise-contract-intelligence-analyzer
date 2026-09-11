"""In-process cosine-similarity vector store. The default backend so the
repo runs with no external database; `qdrant_store.py` / `pgvector_store.py`
show the production swap-in."""
from __future__ import annotations

from app.vectorstore.base import VectorStore


def _cosine(a: list[float], b: list[float]) -> float:
    # HashingEmbedder vectors are already L2-normalized, so the dot product
    # alone equals cosine similarity.
    return sum(x * y for x, y in zip(a, b))


class InMemoryVectorStore(VectorStore):
    def __init__(self) -> None:
        self._items: dict[str, dict] = {}

    def add(self, id: str, vector: list[float], metadata: dict, text: str) -> None:
        self._items[id] = {"vector": vector, "metadata": metadata, "text": text}

    def query(self, vector: list[float], top_k: int = 5) -> list[dict]:
        scored = [
            (item_id, _cosine(vector, item["vector"]), item) for item_id, item in self._items.items()
        ]
        scored.sort(key=lambda t: t[1], reverse=True)
        return [
            {"id": item_id, "score": score, "metadata": item["metadata"], "text": item["text"]}
            for item_id, score, item in scored[:top_k]
        ]
