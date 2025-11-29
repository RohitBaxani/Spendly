from __future__ import annotations

from typing import Any, Dict

from app.llm_client import call_llm


def loan_eligibility(
    monthly_income: float,
    existing_emi: float,
    cibil: int,
) -> Dict[str, Any]:
    """Compute simple EMI and loan eligibility and explain it."""

    max_emi = monthly_income * 0.4 - existing_emi
    if max_emi < 0:
        max_emi = 0.0

    loan_amount = max_emi * 60  # 5-year loan
    interest = 0.12

    prompt = f"""
User monthly income: {monthly_income}
Existing EMIs: {existing_emi}
CIBIL score: {cibil}
Max EMI allowed (40% rule): {max_emi}
Approx loan amount possible (5 yrs @12%): {loan_amount}

Explain:
- Whether banks are likely to approve (assume CIBIL >= 700 is good).
- What loan range looks reasonable for them.
- 3-4 tips to improve approval chances and keep EMI comfortable.
"""

    narrative = call_llm(
        prompt, "You are a bank loan officer explaining in simple language."
    )

    return {
        "max_emi": max_emi,
        "loan_amount": loan_amount,
        "interest_rate_assumed": interest,
        "narrative": narrative,
        "cibil_score": cibil,
    }


