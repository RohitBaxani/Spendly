from __future__ import annotations

import csv
import re
from typing import Any, Dict, List

from app.llm_client import call_llm


KEYWORD_MAP: Dict[str, str] = {
    "zomato": "Food",
    "swiggy": "Food",
    "uber": "Transport",
    "ola": "Transport",
    "rent": "Rent",
    "emi": "EMI",
}


def parse_bank_csv(path: str) -> Dict[str, Any]:
    """Parse bank CSV into structured income + transactions."""

    transactions: List[Dict[str, Any]] = []
    income = 0.0

    with open(path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            desc = row.get("Description") or row.get("desc") or ""
            amount_str = row.get("Amount") or row.get("amount") or "0"
            try:
                amount = float(amount_str)
            except ValueError:
                continue
            date = row.get("Date") or row.get("date") or ""
            category = infer_category(desc, amount)
            transactions.append(
                {
                    "date": date,
                    "desc": desc,
                    "amount": amount,
                    "category": category,
                }
            )
            if amount > 0:
                income += amount

    emergency_fund = max(0.0, income) * 0.25
    return {
        "income": income,
        "transactions": transactions,
        "emergencyFund": emergency_fund,
    }


def infer_category(desc: str, amount: float) -> str:
    d = desc.lower()
    for keyword, cat in KEYWORD_MAP.items():
        if keyword in d:
            return cat

    prompt = f"""
You are categorizing a single bank transaction.

Description: {desc}
Amount: {amount}

Return only a concise category such as:
Food, Groceries, Transport, Rent, EMI, Shopping, Salary, Utilities, Others.
"""
    category = call_llm(
        prompt, "You are a classification engine for bank transactions."
    )
    return (category or "Others").splitlines()[0]


def parse_payslip_text(text: str) -> Dict[str, Any]:
    """Very simple regex-based extraction from payslip text."""

    def find_number(label_pattern: str) -> float:
        match = re.search(
            label_pattern + r".*?(\d[\d,]*)",
            text,
            re.IGNORECASE | re.DOTALL,
        )
        if not match:
            return 0.0
        return float(match.group(1).replace(",", ""))

    basic = find_number("Basic")
    hra = find_number("HRA")
    pf = find_number("PF")
    tds = find_number("TDS|Tax Deducted|Income Tax")

    income = basic + hra
    return {
        "income": income,
        "payslip_info": {
            "basic": basic,
            "hra": hra,
            "pf": pf,
            "tax_deducted": tds,
        },
    }


