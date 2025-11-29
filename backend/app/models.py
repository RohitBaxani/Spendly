from __future__ import annotations

from typing import Any, Dict, List, Literal, Optional

from pydantic import BaseModel


IntentType = Literal["spending_plan", "tax_saver", "investment", "loan"]


class ChatMessage(BaseModel):
    role: Literal["user", "assistant", "system"]
    content: str


class ChatRequest(BaseModel):
    session_id: str
    message: str
    intent: Optional[IntentType] = None
    cibil_score: Optional[int] = None
    file_path: Optional[str] = None
    metadata: Dict[str, Any] = {}


class ChatResponse(BaseModel):
    session_id: str
    messages: List[ChatMessage]
    summary: Optional[str] = None
    data: Optional[Dict[str, Any]] = None


class Transaction(BaseModel):
    date: str
    desc: str
    amount: float
    category: str


class ParsedDocument(BaseModel):
    income: float
    transactions: List[Transaction] = []
    emergencyFund: float = 0.0
    payslip_info: Dict[str, Any] = {}


