from __future__ import annotations

from collections import defaultdict
from typing import Any, Dict

from app.llm_client import call_llm


def build_spending_plan(parsed: Dict[str, Any]) -> Dict[str, Any]:
    """Compute spending summary, red flags, and suggested plan."""

    income = float(parsed.get("income", 0.0))
    txs = parsed.get("transactions", [])

    category_totals: Dict[str, float] = defaultdict(float)
    total_expense = 0.0

    for t in txs:
        amt = float(t.get("amount", 0.0))
        if amt < 0:
            total_expense += -amt
            category_totals[str(t.get("category", "Others"))] += -amt

    category_percent = {
        cat: (val / total_expense * 100 if total_expense else 0.0)
        for cat, val in category_totals.items()
    }

    flags = []
    if category_percent.get("Food", 0.0) > 20.0:
        flags.append("HIGH FOOD DELIVERY / dining – more than 20% of expenses.")
    if category_totals.get("EMI", 0.0) > income * 0.4:
        flags.append("HIGH EMI BURDEN – more than 40% of income.")
    if float(parsed.get("emergencyFund", 0.0)) < income * 2:
        flags.append("LOW EMERGENCY FUND – less than 2 months of income saved.")

    prompt = f"""
You are a disciplined but friendly Indian personal finance coach.

CONTEXT
- Monthly income (approx): {income}
- Total monthly expenses: {total_expense}
- Category % spend: {category_percent}
- Detected red flags: {flags}

INSTRUCTIONS
- Audience is an Indian salaried person in their 20s or 30s.
- Be practical and conservative; do not promise guaranteed returns.
- Do not recommend specific stock symbols, broker apps, or banks.
- You may mention only broad product types (index fund, debt fund, FD, gold ETF).
- Never ask the user to borrow to invest.

OUTPUT FORMAT (PLAIN TEXT, NO MARKDOWN)
- First line: one-sentence high-level assessment (short).
- Then 3 bullet points for an ideal monthly budget split (percentages by broad bucket).
- Then 1 bullet with an approximate SIP amount and why it is reasonable.
- Then 4–6 bullets with lifestyle adjustments, each starting with "- ".
- Keep each bullet to max 2 short sentences.
- Do NOT use markdown syntax like **bold** or numbered lists; only plain text bullets.
"""
    narrative = call_llm(prompt)

    return {
        "income": income,
        "total_expense": total_expense,
        "category_percent": category_percent,
        "red_flags": flags,
        "narrative": narrative,
    }


