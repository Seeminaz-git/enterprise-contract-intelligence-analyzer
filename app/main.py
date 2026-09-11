"""FastAPI app exposing contract ingestion, risk analysis, and Q&A.

Run locally with:  uvicorn app.main:app --reload
"""
from __future__ import annotations

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from app.analyzer import ContractAnalyzer

app = FastAPI(title="Enterprise Contract Intelligence Analyzer")
analyzer = ContractAnalyzer()
_analyses: dict[str, object] = {}


class ContractSubmission(BaseModel):
    contract_id: str
    raw_text: str


class ContractQuestion(BaseModel):
    question: str


@app.post("/contracts")
def submit_contract(payload: ContractSubmission):
    analysis = analyzer.analyze(payload.contract_id, payload.raw_text)
    _analyses[payload.contract_id] = analysis
    return {
        "contract_id": analysis.contract_id,
        "total_risk_flags": analysis.total_risk_flags,
        "clauses": [
            {"clause_type": c.clause_type, "text": c.text, "risk_flags": c.risk_flags} for c in analysis.clauses
        ],
    }


@app.post("/contracts/{contract_id}/query")
def query_contract(contract_id: str, payload: ContractQuestion):
    if contract_id not in _analyses:
        raise HTTPException(status_code=404, detail=f"No contract ingested with id '{contract_id}'")

    results = analyzer.query(contract_id, payload.question)
    return {"contract_id": contract_id, "question": payload.question, "matches": results}


@app.get("/health")
def health():
    return {"status": "ok"}


if __name__ == "__main__":
    import os

    with open(os.path.join(os.path.dirname(__file__), "..", "data", "sample_service_agreement.txt")) as f:
        text = f.read()

    analysis = analyzer.analyze("SAMPLE-1", text)
    for clause in analysis.clauses:
        print(f"[{clause.clause_type}] {clause.text.splitlines()[0]}")
        for flag in clause.risk_flags:
            print(f"  RISK: {flag}")
