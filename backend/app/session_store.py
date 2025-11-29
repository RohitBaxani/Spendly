from __future__ import annotations

import json
import os
from typing import Any, Dict

from app.config import settings


os.makedirs(settings.sessions_dir, exist_ok=True)


def _path(session_id: str) -> str:
    return os.path.join(settings.sessions_dir, f"{session_id}.json")


def load_session(session_id: str) -> Dict[str, Any]:
    path = _path(session_id)
    if not os.path.exists(path):
        return {"messages": [], "state": {}}
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_session(session_id: str, data: Dict[str, Any]) -> None:
    path = _path(session_id)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


