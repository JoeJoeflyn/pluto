"""
Spending statistics aggregation.

Filters by month/year; optionally returns a per-category breakdown sorted
by total spend descending.
"""
from __future__ import annotations

from typing import Optional

from sqlalchemy import extract, func
from sqlalchemy.orm import Session

from core.database import Expense


def spending_stats(
    db: Session,
    month: Optional[int] = None,
    year: Optional[int] = None,
    include_category_breakdown: bool = False,
) -> dict:
    query = db.query(Expense)
    if month is not None:
        query = query.filter(extract("month", Expense.date) == month)
    if year is not None:
        query = query.filter(extract("year", Expense.date) == year)

    total = (
        query.with_entities(func.coalesce(func.sum(Expense.amount), 0.0)).scalar()
        or 0.0
    )
    count = query.count()

    breakdown = []
    if include_category_breakdown:
        rows = (
            query.with_entities(
                Expense.category,
                func.coalesce(func.sum(Expense.amount), 0.0).label("total"),
                func.count(Expense.id).label("cnt"),
            )
            .group_by(Expense.category)
            .order_by(func.sum(Expense.amount).desc())
            .all()
        )
        breakdown = [
            {
                "category": row[0] or "Uncategorized",
                "total": float(row[1]),
                "count": int(row[2]),
            }
            for row in rows
        ]

    return {
        "total": float(total),
        "count": int(count),
        "by_category": breakdown,
        "filters": {
            "month": month,
            "year": year,
            "category_breakdown": include_category_breakdown,
        },
    }
