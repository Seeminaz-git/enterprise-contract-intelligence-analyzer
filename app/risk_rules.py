"""Per-clause-type risk heuristics.

Deliberately simple, transparent rules for a demo; a production system would
layer an LLM risk-review prompt on top of (or instead of) these, using them
as a fast, explainable first pass that catches the most common red flags.
"""
from __future__ import annotations

import re


def check_termination(text: str) -> list[str]:
    flags = []
    if re.search(r"automatically renew", text, re.IGNORECASE) and "notice" not in text.lower():
        flags.append("Auto-renewal clause does not specify a notice period to opt out.")
    return flags


def check_liability(text: str) -> list[str]:
    flags = []
    if re.search(r"\bunlimited\b", text, re.IGNORECASE):
        flags.append("Liability is unlimited, exposing the counterparty to uncapped damages.")
    return flags


def check_confidentiality(text: str) -> list[str]:
    return []


def check_payment_terms(text: str) -> list[str]:
    flags = []
    match = re.search(r"(\d+(?:\.\d+)?)\s*%\s*per month", text, re.IGNORECASE)
    if match and float(match.group(1)) > 1.5:
        flags.append(
            f"Late-payment interest rate of {match.group(1)}% per month may exceed typical "
            "market caps (commonly ~1.5%/month)."
        )
    return flags


def check_governing_law(text: str) -> list[str]:
    return []


RISK_CHECKERS = {
    "termination": check_termination,
    "liability": check_liability,
    "confidentiality": check_confidentiality,
    "payment_terms": check_payment_terms,
    "governing_law": check_governing_law,
}


def get_risk_flags(clause_type: str, text: str) -> list[str]:
    checker = RISK_CHECKERS.get(clause_type)
    return checker(text) if checker else []
