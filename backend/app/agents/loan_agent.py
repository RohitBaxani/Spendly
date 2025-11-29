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
You are a cautious Indian bank loan officer explaining in simple language.

CONTEXT
- Monthly income: {monthly_income}
- Existing EMIs: {existing_emi}
- CIBIL score: {cibil}
- Max EMI allowed by 40% rule: {max_emi}
- Approx loan amount possible (5 yrs @12%): {loan_amount}

GUARDRAILS
- Treat all amounts as rough eligibility, not a promise or sanction.
- Make it clear that every bank has its own policy and this is only an estimate.
- Do not suggest hiding liabilities or gaming the system.

OUTPUT FORMAT (PLAIN TEXT, NO MARKDOWN)
- First line: 1 short sentence like "You can roughly afford a loan of around X."
- Then bullets starting with "- ":
  - whether CIBIL is generally acceptable or needs improvement,
  - what EMI range looks comfortable vs risky,
  - 3–4 tips to improve approval chances (e.g., close small loans, reduce card utilisation),
  - 1 bullet warning not to over-stretch EMIs.
- Keep each bullet to max 2 sentences.
- Do NOT use **bold** or markdown formatting.
"""

    narrative = call_llm(prompt)

    return {
        "max_emi": max_emi,
        "loan_amount": loan_amount,
        "interest_rate_assumed": interest,
        "narrative": narrative,
        "cibil_score": cibil,
    }


