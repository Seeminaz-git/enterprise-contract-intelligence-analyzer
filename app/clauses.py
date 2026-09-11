"""Clause segmentation and classification.

Real contracts arrive as PDFs — a production ingestion step would run
pypdf/pdfplumber to extract text first; this repo takes already-extracted
plain text (`data/*.txt`) as its input so the clause-analysis logic is
testable without shipping a binary PDF fixture. Classification is
keyword-based so it runs with no LLM API key; a production build would swap
this for an LLM classification prompt over each clause.
"""
from __future__ import annotations

CLAUSE_KEYWORDS: dict[str, list[str]] = {
    "termination": ["terminat", "renew"],
    "liability": ["liability", "liable", "negligence", "limitation of liability"],
    "confidentiality": ["confidential", "non-disclosure", "proprietary", "disclose"],
    "payment_terms": ["payment", "invoice", "fee", "interest"],
    "governing_law": ["governing law", "jurisdiction", "venue"],
}


def split_into_clauses(raw_text: str) -> list[str]:
    return [p.strip() for p in raw_text.split("\n\n") if p.strip()]


def classify_clause(text: str) -> str:
    text_lower = text.lower()
    best_type = "general"
    best_hits = 0
    for clause_type, keywords in CLAUSE_KEYWORDS.items():
        hits = sum(1 for kw in keywords if kw in text_lower)
        if hits > best_hits:
            best_type = clause_type
            best_hits = hits
    return best_type
