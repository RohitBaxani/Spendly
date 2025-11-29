from __future__ import annotations

from typing import Optional

import google.generativeai as genai

from app.config import settings


_configured = False


def _ensure_configured() -> None:
    global _configured
    if _configured:
        return
    genai.configure(api_key=settings.google_api_key)
    _configured = True


def call_llm(prompt: str, system_instructions: Optional[str] = None) -> str:
    """Call Gemini model with simple text prompt and optional system guidance."""

    _ensure_configured()

    model = genai.GenerativeModel(settings.model_name)
    if system_instructions:
        prompt = f"{system_instructions}\n\n{prompt}"
    response = model.generate_content(prompt)
    # Defensive: handle potential missing text
    return (getattr(response, "text", "") or "").strip()


