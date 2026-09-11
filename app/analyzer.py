from __future__ import annotations

from dataclasses import dataclass

from app.clauses import classify_clause, split_into_clauses
from app.embeddings import Embedder, HashingEmbedder
from app.risk_rules import get_risk_flags
from app.vectorstore import get_vector_store
from app.vectorstore.base import VectorStore


@dataclass
class ClauseFinding:
    clause_type: str
    text: str
    risk_flags: list[str]


@dataclass
class ContractAnalysis:
    contract_id: str
    clauses: list[ClauseFinding]
    total_risk_flags: int


class ContractAnalyzer:
    def __init__(self, vector_store: VectorStore | None = None, embedder: Embedder | None = None):
        self.vector_store = vector_store or get_vector_store()
        self.embedder = embedder or HashingEmbedder()

    def analyze(self, contract_id: str, raw_text: str) -> ContractAnalysis:
        findings: list[ClauseFinding] = []

        for idx, clause_text in enumerate(split_into_clauses(raw_text)):
            clause_type = classify_clause(clause_text)
            risk_flags = get_risk_flags(clause_type, clause_text)
            findings.append(ClauseFinding(clause_type=clause_type, text=clause_text, risk_flags=risk_flags))

            vector = self.embedder.embed(clause_text)
            self.vector_store.add(
                id=f"{contract_id}:{idx}",
                vector=vector,
                metadata={"contract_id": contract_id, "clause_type": clause_type},
                text=clause_text,
            )

        total_flags = sum(len(f.risk_flags) for f in findings)
        return ContractAnalysis(contract_id=contract_id, clauses=findings, total_risk_flags=total_flags)

    def query(self, contract_id: str, question: str, top_k: int = 2) -> list[dict]:
        vector = self.embedder.embed(question)
        # Over-fetch then filter to this contract, since the in-memory store
        # (and a real vector DB without a metadata filter wired up) searches
        # across every ingested contract's clauses.
        results = self.vector_store.query(vector, top_k=top_k * 10)
        filtered = [r for r in results if r["metadata"]["contract_id"] == contract_id]
        return filtered[:top_k]
