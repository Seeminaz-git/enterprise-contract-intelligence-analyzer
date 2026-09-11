"""pgvector-backed vector store (PostgreSQL + the pgvector extension) for
production deployments."""
from __future__ import annotations

import os

from app.vectorstore.base import VectorStore


class PgVectorStore(VectorStore):
    def __init__(self, dsn: str | None = None, table: str = "contract_clauses"):
        self.dsn = dsn or os.environ.get("PG_DSN")
        self.table = table
        if not self.dsn:
            raise RuntimeError("PG_DSN not configured")

        # Production implementation, assuming a table created with:
        #
        #   CREATE EXTENSION IF NOT EXISTS vector;
        #   CREATE TABLE contract_clauses (
        #       id TEXT PRIMARY KEY, embedding VECTOR(128), metadata JSONB, text TEXT
        #   );
        #
        #   import psycopg2
        #   self.conn = psycopg2.connect(self.dsn)
        raise NotImplementedError("Wire up psycopg2 against a live pgvector-enabled Postgres instance")

    def add(self, id: str, vector: list[float], metadata: dict, text: str) -> None:
        # cursor.execute(
        #     "INSERT INTO contract_clauses (id, embedding, metadata, text) VALUES (%s, %s, %s, %s) "
        #     "ON CONFLICT (id) DO UPDATE SET embedding = EXCLUDED.embedding",
        #     (id, vector, json.dumps(metadata), text),
        # )
        raise NotImplementedError

    def query(self, vector: list[float], top_k: int = 5) -> list[dict]:
        # cursor.execute(
        #     "SELECT id, metadata, text, 1 - (embedding <=> %s) AS score "
        #     "FROM contract_clauses ORDER BY embedding <=> %s LIMIT %s",
        #     (vector, vector, top_k),
        # )
        raise NotImplementedError
