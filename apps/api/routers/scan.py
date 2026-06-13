"""
Receipt scanning endpoint.

Uploads an image, runs the AI extractor, returns the parsed fields
*without* writing to the database. The client confirms/edits and POSTs
to /expenses. This matches the spec's two-step data flow.
"""
from __future__ import annotations

import os
import shutil
import uuid

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.orm import Session

from core.config import ALLOWED_IMAGE_EXT, RECEIPTS_DIR
from core.database import get_db
from models.schemas import ScanOut
from services.ai_service import extract_receipt_data

router = APIRouter(tags=["scan"])


def _missing_fields(extracted: dict) -> list[str]:
    """Surface fields the AI couldn't fill so the UI can prompt the user."""
    missing = []
    if not extracted.get("date"):
        missing.append("date")
    if extracted.get("amount") in (None, 0):
        missing.append("amount")
    if not extracted.get("merchant"):
        missing.append("merchant")
    return missing


def _resolve_image_path(filename: str) -> str:
    """Sanitize the upload filename before we write to disk."""
    ext = os.path.splitext(filename)[1].lower()
    if ext not in ALLOWED_IMAGE_EXT:
        raise HTTPException(
            status_code=400,
            detail=(
                f"Unsupported image type '{ext}'. "
                "Allowed: jpg, jpeg, png, webp, gif, bmp."
            ),
        )
    return os.path.join(RECEIPTS_DIR, f"{uuid.uuid4()}{ext}")


@router.post("/scan", response_model=ScanOut)
async def scan_receipt(file: UploadFile = File(...), db: Session = Depends(get_db)):
    file_path = _resolve_image_path(file.filename or "receipt.jpg")

    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except OSError as exc:
        raise HTTPException(status_code=500, detail=f"Failed to save image: {exc}")

    extraction = extract_receipt_data(file_path)
    return ScanOut(
        image_path=file_path,
        extracted=extraction.data,
        errors=extraction.errors,
        needs_review=_missing_fields(extraction.data),
    )
