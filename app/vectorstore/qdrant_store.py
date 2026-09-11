"""Qdrant-backed vector store for production deployments."""
from __future__ import annotations

import os

from app.vectorstore.base import VectorStore


class QdrantVectorStore(VectorStore):
    def __init__(self, url: str | None = None, collection: str = "contract_clauses", dimensions: int = 128):
        self.url = url or os.environ.get("QDRANT_URL")
        self.collection = collection
        self.dimensions = dimensions
        if not self.url:
            raise RuntimeError("QDRANT_URL not configured")

        # Production implementation:
        #
        #   from qdrant_client import QdrantClient
        #   from qdrant_client.models import Distance, VectorParams, PointStruct
        #
        #   self.client = QdrantClient(url=self.url)
        #   self.client.recreate_collection(
        #       collection_name=self.collection,
        #       vectors_config=VectorParams(size=self.dimensions, distance=Distance.COSINE),
        #   )
        raise NotImplementedError("Wire up qdrant-client against a live Qdrant instance")

    def add(self, id: str, vector: list[float], metadata: dict, text: str) -> None:
        # self.client.upsert(self.collection, points=[PointStruct(id=id, vector=vector,
        #     payload={**metadata, "text": text})])
        raise NotImplementedError

    def query(self, vector: list[float], top_k: int = 5) -> list[dict]:
        # hits = self.client.search(self.collection, query_vector=vector, limit=top_k)
        # return [{"id": h.id, "score": h.score, "metadata": h.payload, "text": h.payload["text"]} for h in hits]
        raise NotImplementedError
