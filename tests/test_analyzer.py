import os

import pytest

from app.analyzer import ContractAnalyzer

DATA_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "sample_service_agreement.txt")


@pytest.fixture(scope="module")
def sample_text():
    with open(DATA_PATH, "r", encoding="utf-8") as f:
        return f.read()


def test_classifies_all_five_clause_types(sample_text):
    analyzer = ContractAnalyzer()
    analysis = analyzer.analyze("C1", sample_text)

    clause_types = [c.clause_type for c in analysis.clauses]
    assert clause_types == ["termination", "liability", "confidentiality", "payment_terms", "governing_law"]


def test_flags_auto_renewal_without_notice_period(sample_text):
    analyzer = ContractAnalyzer()
    analysis = analyzer.analyze("C1", sample_text)

    termination_clause = next(c for c in analysis.clauses if c.clause_type == "termination")
    assert any("notice period" in flag for flag in termination_clause.risk_flags)


def test_flags_unlimited_liability(sample_text):
    analyzer = ContractAnalyzer()
    analysis = analyzer.analyze("C1", sample_text)

    liability_clause = next(c for c in analysis.clauses if c.clause_type == "liability")
    assert any("unlimited" in flag.lower() for flag in liability_clause.risk_flags)


def test_flags_high_late_payment_interest_rate(sample_text):
    analyzer = ContractAnalyzer()
    analysis = analyzer.analyze("C1", sample_text)

    payment_clause = next(c for c in analysis.clauses if c.clause_type == "payment_terms")
    assert any("5%" in flag for flag in payment_clause.risk_flags)
    assert analysis.total_risk_flags == 3


def test_query_retrieves_the_relevant_clause(sample_text):
    analyzer = ContractAnalyzer()
    analyzer.analyze("C1", sample_text)

    matches = analyzer.query("C1", "What is the late payment interest rate?", top_k=1)

    assert len(matches) == 1
    assert matches[0]["metadata"]["clause_type"] == "payment_terms"
    assert "5%" in matches[0]["text"]


def test_query_is_scoped_to_the_requested_contract(sample_text):
    analyzer = ContractAnalyzer()
    analyzer.analyze("C1", sample_text)
    analyzer.analyze("C2", sample_text)

    matches = analyzer.query("C2", "governing law jurisdiction", top_k=5)

    assert matches
    assert all(m["metadata"]["contract_id"] == "C2" for m in matches)
