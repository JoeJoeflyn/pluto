"""
Normalized merchant list — deduped rows, most-visited first.
"""
from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from core.database import get_db
from models.schemas import MerchantOut
from services import merchant_service

router = APIRouter(tags=["merchants"])


@router.get("/merchants", response_model=list[MerchantOut])
def list_merchants(db: Session = Depends(get_db)):
    rows = merchant_service.list_merchants(db)
    return [MerchantOut.model_validate(m) for m in rows]
