"""
Category queries. Categories are pre-seeded at startup and rarely change.
"""
from __future__ import annotations

from typing import List

from sqlalchemy.orm import Session

from core.database import Category


def list_categories(db: Session) -> List[Category]:
    """All categories, stable order by id (matches seed order)."""
    return db.query(Category).order_by(Category.id).all()
