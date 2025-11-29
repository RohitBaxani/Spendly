from __future__ import annotations

import os
import sys
import uuid
from typing import Optional

from fastapi import FastAPI, File, Form, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

if __package__ in (None, ""):
    CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
    PARENT_DIR = os.path.dirname(CURRENT_DIR)
    if PARENT_DIR not in sys.path:
        sys.path.insert(0, PARENT_DIR)

from app.config import settings
from app.orchestrator import run_turn


app = FastAPI(title="Spendly POC Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:4200", "http://localhost:5173", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

os.makedirs(settings.uploads_dir, exist_ok=True)


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.post("/upload")
async def upload_file(file: UploadFile = File(...)) -> dict:
    file_id = str(uuid.uuid4())
    _, ext = os.path.splitext(file.filename)
    path = os.path.join(settings.uploads_dir, file_id + ext)
    contents = await file.read()
    with open(path, "wb") as f:
        f.write(contents)
    return {"file_id": file_id, "filename": file.filename, "path": path}


@app.post("/chat")
async def chat(
    session_id: str = Form(...),
    message: str = Form(...),
    intent: str = Form(...),
    file_path: Optional[str] = Form(None),
    cibil_score: Optional[int] = Form(None),
    monthly_income: Optional[float] = Form(None),
    existing_emi: Optional[float] = Form(None),
) -> JSONResponse:
    metadata: dict = {}
    if cibil_score is not None:
        metadata["cibil_score"] = cibil_score
    if monthly_income is not None:
        metadata["monthly_income"] = monthly_income
    if existing_emi is not None:
        metadata["existing_emi"] = existing_emi

    result = run_turn(session_id, intent, message, file_path, metadata)
    return JSONResponse(result)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)


