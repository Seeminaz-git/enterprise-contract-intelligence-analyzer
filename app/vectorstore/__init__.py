import os

from app.vectorstore.base import VectorStore
from app.vectorstore.memory import InMemoryVectorStore


def get_vector_store() -> VectorStore:
    if os.environ.get("QDRANT_URL"):
        from app.vectorstore.qdrant_store import QdrantVectorStore

        return QdrantVectorStore()
    if os.environ.get("PG_DSN"):
        from app.vectorstore.pgvector_store import PgVectorStore

        return PgVectorStore()
    return InMemoryVectorStore()
