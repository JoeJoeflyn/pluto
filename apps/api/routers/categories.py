"""
Pre-seeded category list (Food & Dining, Shopping, …).
"""
from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from core.database import get_db
from models.schemas import CategoryOut
from services import category_service

router = APIRouter(tags=["categories"])


@router.get("/categories", response_model=list[CategoryOut])
def list_categories(db: Session = Depends(get_db)):
    rows = category_service.list_categories(db)
    return [CategoryOut.model_validate(c) for c in rows]
