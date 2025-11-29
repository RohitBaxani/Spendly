from __future__ import annotations

from typing import Any, Dict

from app.llm_client import call_llm


def build_investment_plan(parsed: Dict[str, Any]) -> Dict[str, Any]:
    """Allocate surplus into simple buckets and explain."""

    income = float(parsed.get("income", 0.0))
    txs = parsed.get("transactions", [])

    total_expense = 0.0
    for t in txs:
        amt = float(t.get("amount", 0.0))
        if amt < 0:
            total_expense += -amt

    surplus = max(0.0, income - total_expense)
    emergency_fund = float(parsed.get("emergencyFund", 0.0))
    min_emergency = income * 3

    can_invest = max(0.0, surplus - max(0.0, min_emergency - emergency_fund) / 12.0)

    equity = can_invest * 0.6
    debt = can_invest * 0.2
    gold = can_invest * 0.1
    liquid = can_invest * 0.1

    mock_market = {
        "nifty_50": {"1y_return": 0.14},
        "short_term_debt": {"1y_return": 0.07},
        "gold": {"1y_return": 0.10},
        "liquid_fund": {"1y_return": 0.05},
    }

    prompt = f"""
You are a calm, long-term focused investment advisor for Indian salaried users.

CONTEXT
- Monthly income: {income}
- Total expenses: {total_expense}
- Monthly surplus: {surplus}
- Existing emergency fund: {emergency_fund}
- Minimum recommended emergency fund (~3 months): {min_emergency}

Proposed monthly allocation from investible surplus:
- Equity index SIP: {equity}
- Debt / FD: {debt}
- Gold: {gold}
- Liquid fund: {liquid}

Mock market data (approx 1y return): {mock_market}

GUARDRAILS
- Do NOT recommend specific stock symbols, PMS, or individual mutual fund names.
- Only use broad types: index fund, flexi-cap, debt fund, FD, gold ETF, liquid fund.
- Make it clear that returns are not guaranteed and are just historical examples.
- Do not encourage taking loans or using credit cards to invest.

OUTPUT FORMAT (PLAIN TEXT, NO MARKDOWN)
- First line: 1 short sentence summarising the overall plan.
- Then 4–6 bullets starting with "- ":
  - explain why this split is balanced,
  - how to prioritise building emergency fund vs investing,
  - what exact actions to start this month (e.g., "start a SIP of X in a low-cost index fund").
- Keep each bullet to max 2 short sentences.
- Do NOT use markdown like **bold**, numbered lists, or tables.
"""

    narrative = call_llm(prompt)

    return {
        "income": income,
        "total_expense": total_expense,
        "surplus": surplus,
        "investible": can_invest,
        "allocation": {
            "equity_sip": equity,
            "debt_fd": debt,
            "gold": gold,
            "liquid": liquid,
        },
        "mock_market": mock_market,
        "narrative": narrative,
    }


