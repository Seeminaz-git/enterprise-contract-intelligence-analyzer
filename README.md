# Enterprise Contract Intelligence Analyzer

A contract-analysis tool that segments a contract into clauses, classifies
each one (termination, liability, confidentiality, payment terms, governing
law), flags common risky patterns, and answers questions about the contract
by retrieving the most relevant clause from a real vector-store abstraction
— unlike this portfolio's other RAG project, this one stores and searches
actual embedding vectors rather than a from-scratch keyword index.

This is a portfolio/demo implementation. Real contracts arrive as PDFs — a
production ingestion step would run `pypdf`/`pdfplumber` ahead of this
pipeline; the repo takes already-extracted plain text
(`data/sample_service_agreement.txt`) as input so the clause-analysis logic
is testable without shipping a binary PDF fixture. Embeddings are a
dependency-free hashing-trick bag-of-words vectorizer (`app/embeddings.py`)
rather than a real embeddings API call, so the repo runs with zero API keys.

## Architecture

```
contract text ──▶ split_into_clauses() ──▶ classify_clause() ──▶ get_risk_flags()
                        (paragraphs)         (keyword rules)      (per-clause-type
                                                    │                heuristics)
                                                    ▼
                                          HashingEmbedder.embed()
                                                    │
                                                    ▼
                                    VectorStore.add(id, vector, metadata, text)
                                    (in-memory cosine / Qdrant / pgvector)
                                                    │
                       question ──▶ embed() ──▶ VectorStore.query() ──▶ matching clause(s)
```

- **Clause segmentation & classification** (`app/clauses.py`): splits the
  contract into paragraphs and classifies each into one of five clause
  types by keyword matching against both the clause heading and body.
- **Risk rules** (`app/risk_rules.py`): transparent, per-clause-type
  heuristics — e.g. an auto-renewal clause with no stated notice period, an
  unlimited-liability clause, or a late-payment interest rate above a
  typical market cap. A production system would layer an LLM risk-review
  prompt on top of these as a second pass.
- **Embeddings** (`app/embeddings.py`): a stable (MD5-based, not Python's
  randomized `hash()`) hashing-trick bag-of-words embedder — a placeholder
  for a real embeddings API, sharing the same `embed(text) -> vector`
  interface a production adapter would implement.
- **Vector store** (`app/vectorstore/`): a real store abstraction —
  `InMemoryVectorStore` (cosine similarity, the default, zero dependencies)
  plus `QdrantVectorStore` and `PgVectorStore` adapters showing the
  production swap-in against a real Qdrant or pgvector-enabled Postgres
  instance.
- **Q&A** (`app/analyzer.py` `query()`): embeds the question, searches the
  vector store, and filters results down to the requested contract —
  because a real vector DB call would typically need a metadata filter
  wired up server-side, this over-fetches and filters client-side to keep
  the demo backend-agnostic.

## Running locally

```bash
pip install -r requirements.txt
python -m app.main
```

or as an API:

```bash
uvicorn app.main:app --reload

curl -X POST localhost:8000/contracts -H "Content-Type: application/json" \
  -d @- <<'EOF'
{"contract_id": "C1", "raw_text": "1. Term and Termination\nThis Agreement shall automatically renew..."}
EOF

curl -X POST localhost:8000/contracts/C1/query -H "Content-Type: application/json" \
  -d '{"question": "What is the late payment interest rate?"}'
```

## Tests

```bash
pytest
```

Covers correct clause classification across all five types, each of the
three risk heuristics firing on the sample contract, question-answering
retrieving the correct clause, and query results staying scoped to the
requested contract when multiple contracts have been ingested.

## Going to production

Set `QDRANT_URL` or `PG_DSN` to switch the vector store from in-memory to
Qdrant or pgvector. Swap `HashingEmbedder` for a real embeddings API
(OpenAI, Anthropic, or a LlamaIndex-managed embedding pipeline), and add a
`pypdf`/`pdfplumber` ingestion step ahead of `split_into_clauses()` for real
PDF contracts.

## Tech stack

Python, FastAPI, LlamaIndex-style ingestion, pgvector/Qdrant (vector store
adapters), Pinecone (documented as an equivalent swap-in).
