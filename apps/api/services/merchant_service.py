"""
Merchant domain logic.

Merchants are deduped by (name, address) so repeated receipts from the same
store share a single row. `visit_count` increments and `last_seen` updates
on every match. Phone/email are stored once on the merchant row.
"""
from __future__ import annotations

import datetime
from typing import List, Optional

from sqlalchemy.orm import Session

from core.database import Merchant


def upsert_merchant(
    db: Session,
    name: str,
    address: Optional[str] = None,
    phone: Optional[str] = None,
    email: Optional[str] = None,
) -> Optional[Merchant]:
    """
    Find or create a merchant by (name, address). Increments visit_count
    and updates last_seen on match. Returns the Merchant row, or None if
    no name was provided.
    """
    if not name:
        return None

    existing = (
        db.query(Merchant)
        .filter(Merchant.name == name, Merchant.address == address)
        .first()
    )
    if existing:
        existing.visit_count = (existing.visit_count or 1) + 1
        existing.last_seen = datetime.date.today()
        if phone and not existing.phone:
            existing.phone = phone
        if email and not existing.email:
            existing.email = email
        return existing

    merchant = Merchant(
        name=name,
        address=address,
        phone=phone,
        email=email,
        first_seen=datetime.date.today(),
        last_seen=datetime.date.today(),
    )
    db.add(merchant)
    db.flush()
    return merchant


def list_merchants(db: Session) -> List[Merchant]:
    """All merchants, most-visited first."""
    return db.query(Merchant).order_by(Merchant.visit_count.desc()).all()
