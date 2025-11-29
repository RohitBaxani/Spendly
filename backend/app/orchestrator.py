from __future__ import annotations

from typing import Any, Dict, Optional

from app.agents.document_parser import parse_bank_csv
from app.agents.investment_agent import build_investment_plan
from app.agents.loan_agent import loan_eligibility
from app.agents.spending_agent import build_spending_plan
from app.agents.tax_agent import (
    compute_tax_plan,
    get_next_question,
    record_tax_answer,
)
from app.llm_client import call_llm
from app.session_store import load_session, save_session


def run_turn(
    session_id: str,
    intent: str,
    message: str,
    file_path: Optional[str],
    metadata: Dict[str, Any],
) -> Dict[str, Any]:
    """Single conversational turn orchestration."""

    session = load_session(session_id)
    state = session.get("state", {})
    messages = session.get("messages", [])

    messages.append({"role": "user", "content": message})

    result: Dict[str, Any] = {}

    if intent == "spending_plan":
        if file_path:
            parsed = parse_bank_csv(file_path)
            state["parsed_bank"] = parsed
        parsed = state.get("parsed_bank") or {}
        result = build_spending_plan(parsed)

    elif intent == "tax_saver":
        # Assume income from previous parsed doc or fallback
        annual_income = metadata.get("annual_income") or state.get(
            "annual_income", 6_00_000.0
        )

        # If there is an outstanding question, record the latest answer
        if state.get("awaiting_tax_answer"):
            record_tax_answer(state, message)
            state["awaiting_tax_answer"] = False

        q = get_next_question(state)
        if q:
            state["awaiting_tax_answer"] = True
            result = {"follow_up_question": q}
        else:
            result = compute_tax_plan(state, float(annual_income))

    elif intent == "investment":
        parsed = state.get("parsed_bank") or {}
        result = build_investment_plan(parsed)

    elif intent == "loan":
        monthly_income = float(
            metadata.get("monthly_income") or state.get("monthly_income") or 0.0
        )
        existing_emi = float(metadata.get("existing_emi") or 0.0)
        cibil_score = int(metadata.get("cibil_score") or 0)
        result = loan_eligibility(monthly_income, existing_emi, cibil_score)

    summary_prompt = f"""
You are Spendly, a clear and concise personal finance assistant.

CONTEXT
- Latest user message: {message}
- Agent result JSON (may contain numbers and flags): {result}

TASK
- Summarise the key insights for the user in a way that feels like a WhatsApp chat reply.

OUTPUT FORMAT (PLAIN TEXT, NO MARKDOWN)
- First line: 1 short sentence summarising the situation in plain language.
- Then 3–6 bullets starting with "- " that:
  - highlight the 2–3 most important numbers or flags,
  - suggest next actions the user can take this month,
  - avoid jargon.
- Keep each bullet to max 2 short sentences.
- Do NOT use **bold**, headings, tables, or markdown.
"""
    summary = call_llm(summary_prompt)

    messages.append({"role": "assistant", "content": summary})

    session["messages"] = messages
    session["state"] = state
    save_session(session_id, session)

    return {
        "messages": messages[-8:],
        "summary": summary,
        "data": result,
    }


