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
You are an information extraction engine.

User answer (free text): {user_message}

TASK
- Extract the user's tax-relevant details into a STRICT JSON object.

REQUIRED KEYS
- rent_amount: monthly rent as number (no commas) or null.
- rent_city: string city name or null.
- health_premium: yearly health insurance premium (number) or null.
- has_home_loan: true/false.
- home_loan_emi: monthly home loan EMI (number) or null.
- home_loan_interest_year: yearly interest component (number) or null.

RULES
- If information is not clearly present, set that field to null (do NOT guess).
- Do not add any extra keys.
- Output ONLY valid JSON, no comments, no trailing commas, no explanations.
"""
    parsed = call_llm(prompt)
    state["tax_parsed"] = parsed


def compute_tax_plan(state: Dict[str, Any], annual_income: float) -> Dict[str, Any]:
    """Very rough comparison of old vs new regime for demo."""

    # POC: super-simplified slabs; not real tax logic.
    old_tax = annual_income * 0.15
    new_tax = annual_income * 0.12

    explanation_prompt = f"""
You are an Indian tax consultant explaining in simple Hindi+English mix (Hinglish).

CONTEXT
- Approx annual income: {annual_income}
- Old regime tax (rough): {old_tax}
- New regime tax (rough): {new_tax}
- Parsed user deductions (raw JSON string, may be partial): {state.get("tax_parsed")}

LIMITATIONS
- This is a hackathon demo; you must treat all tax numbers as rough estimates only.
- Do NOT quote exact slab-by-slab sections or pretend to be official advice.
- Clearly state that this is not tax filing advice.

TASK
- Choose which regime (old/new) seems better given deductions and say why.
- Explicitly mention which of these 6 the user is likely under-using or missing:
  80C (investments), 80D (health insurance), HRA (if renting), home loan interest,
  standard deduction, PF contribution.
- Give 3–5 action bullets for next financial year.

OUTPUT FORMAT (PLAIN TEXT, NO MARKDOWN)
- First line: 1 short sentence: "Old regime looks better because ..." or "New regime looks better because ...".
- Then bullets starting with "- " for:
  - regime comparison explanation,
  - missing deductions,
  - suggested next steps.
- Keep bullets concise (max 2 short sentences).
- Do NOT use **bold** or markdown headings.
"""
    explanation = call_llm(explanation_prompt)

    return {
        "old_regime_tax": old_tax,
        "new_regime_tax": new_tax,
        "recommendation": explanation,
    }


