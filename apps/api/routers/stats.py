"""
Spending stats — totals and (optionally) per-category breakdown.
"""
from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from core.database import get_db
from models.schemas import StatsOut
from services import stats_service

router = APIRouter(tags=["stats"])


@router.get("/stats", response_model=StatsOut)
def get_stats(
    month: int | None = Query(None, ge=1, le=12),
    year: int | None = Query(None, ge=1970, le=9999),
    category: bool = Query(False, description="Include per-category breakdown"),
    db: Session = Depends(get_db),
):
    return stats_service.spending_stats(db, month, year, category)
