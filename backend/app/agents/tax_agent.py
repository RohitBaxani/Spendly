from __future__ import annotations

from typing import Any, Dict, List, Tuple

from app.llm_client import call_llm


QUESTIONS: List[Tuple[str, str]] = [
    ("rent", "Do you pay rent? If yes, how much per month and which city?"),
    (
        "health_insurance",
        "Do you pay for health insurance premiums? If yes, how much per year?",
    ),
    ("loans", "Do you have any home loan or education loan? If yes, EMI and amount?"),
]


def get_next_question(state: Dict[str, Any]) -> str | None:
    answers = state.setdefault("tax_questions", {})
    for key, q in QUESTIONS:
        if key not in answers or answers[key] is None:
            return q
    return None


def record_tax_answer(state: Dict[str, Any], user_message: str) -> None:
    """Parse free-form user answer into structured info using LLM."""

    prompt = f"""
User answer: {user_message}

Extract this as JSON with keys:
- rent_amount (monthly, number or null)
- rent_city (string or null)
- health_premium (annual, number or null)
- has_home_loan (true/false)
- home_loan_emi (monthly, number or null)
- home_loan_interest_year (approx yearly interest, number or null)

Missing values can be null.
Only output JSON.
"""
    parsed = call_llm(prompt, "You are an information extraction engine.")
    state["tax_parsed"] = parsed


def compute_tax_plan(state: Dict[str, Any], annual_income: float) -> Dict[str, Any]:
    """Very rough comparison of old vs new regime for demo."""

    # POC: super-simplified slabs; not real tax logic.
    old_tax = annual_income * 0.15
    new_tax = annual_income * 0.12

    explanation = call_llm(
        f"""
Annual income: {annual_income}
Old regime tax (approx): {old_tax}
New regime tax (approx): {new_tax}

User's deductions (raw parsed): {state.get("tax_parsed")}

1. Recommend old vs new regime.
2. List which of these 6 buckets user is missing: 80C, 80D, HRA, home loan interest,
   standard deduction, PF.
3. Give 3-5 bullet actionable tips.

Format in clear bullet points.
""",
        "You are an Indian tax consultant explaining in simple Hindi+English mix.",
    )

    return {
        "old_regime_tax": old_tax,
        "new_regime_tax": new_tax,
        "recommendation": explanation,
    }


