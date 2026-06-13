"""
Expense domain logic.

All CRUD operations on expenses and their line items. Receipts have
many line items (LineItem) and an optional link to a deduped Merchant.
The full set of fields matches the AI extraction output so we can
store whatever the vision model returns without losing fidelity.
"""
from __future__ import annotations

import os
from typing import List, Optional

from sqlalchemy import extract
from sqlalchemy.orm import Session

from core.database import Expense, LineItem
from models.schemas import ExpenseCreate, ExpenseUpdate
from services.merchant_service import upsert_merchant


def expense_to_dict(e: Expense) -> dict:
    """Serialize an Expense row (and its items) into a JSON-safe dict."""
    return {
        "id": e.id,
        "date": e.date.isoformat() if e.date else None,
        "time": e.time,
        "amount": e.amount,
        "currency": e.currency,
        "subtotal": e.subtotal,
        "tax": e.tax,
        "tip": e.tip,
        "discount": e.discount,
        "payment_method": e.payment_method,
        "card_type": e.card_type,
        "card_last4": e.card_last4,
        "cashier": e.cashier,
        "transaction_id": e.transaction_id,
        "reference_id": e.reference_id,
        "auth_id": e.auth_id,
        "address": e.address,
        "phone": e.phone,
        "email": e.email,
        "category": e.category,
        "merchant": e.merchant,
        "merchant_id": e.merchant_id,
        "notes": e.notes or "",
        "image_path": e.image_path or "",
        "raw_text": e.raw_text,
        "created_at": e.created_at.isoformat() if e.created_at else None,
        "updated_at": e.updated_at.isoformat() if e.updated_at else None,
        "synced_at": e.synced_at.isoformat() if e.synced_at else None,
        "line_items": [
            {
                "id": li.id,
                "order_index": li.order_index,
                "name": li.name,
                "price": li.price,
                "quantity": li.quantity,
                "category": li.category,
            }
            for li in (e.items or [])
        ],
    }


def list_expenses(
    db: Session,
    category: Optional[str] = None,
    month: Optional[int] = None,
    year: Optional[int] = None,
    limit: int = 50,
) -> List[Expense]:
    """List expenses, newest first, with optional category/month/year filters."""
    query = db.query(Expense)
    if category:
        query = query.filter(Expense.category == category)
    if month is not None:
        query = query.filter(extract("month", Expense.date) == month)
    if year is not None:
        query = query.filter(extract("year", Expense.date) == year)
    return (
        query.order_by(Expense.date.desc(), Expense.id.desc())
        .limit(limit)
        .all()
    )


def get_expense(db: Session, expense_id: int) -> Optional[Expense]:
    return db.query(Expense).filter(Expense.id == expense_id).first()


def create_expense(db: Session, expense_in: ExpenseCreate) -> Expense:
    """Persist a new expense, deduping the merchant and creating line items."""
    merchant_row = upsert_merchant(
        db,
        name=expense_in.merchant,
        address=expense_in.address,
        phone=expense_in.phone,
        email=expense_in.email,
    )
    db_expense = Expense(
        date=expense_in.date,
        time=expense_in.time,
        amount=expense_in.amount,
        currency=expense_in.currency,
        subtotal=expense_in.subtotal,
        tax=expense_in.tax,
        tip=expense_in.tip,
        discount=expense_in.discount,
        payment_method=expense_in.payment_method,
        card_type=expense_in.card_type,
        card_last4=expense_in.card_last4,
        cashier=expense_in.cashier,
        transaction_id=expense_in.transaction_id,
        reference_id=expense_in.reference_id,
        auth_id=expense_in.auth_id,
        address=expense_in.address,
        phone=expense_in.phone,
        email=expense_in.email,
        category=expense_in.category,
        merchant=expense_in.merchant,
        notes=expense_in.notes,
        image_path=expense_in.image_path,
        raw_text=expense_in.raw_text,
        merchant_id=merchant_row.id if merchant_row else None,
    )
    for idx, item in enumerate(expense_in.line_items or []):
        db_expense.items.append(
            LineItem(
                order_index=idx,
                name=item.name,
                price=item.price,
                quantity=item.quantity,
                category=item.category,
            )
        )
    db.add(db_expense)
    db.commit()
    db.refresh(db_expense)
    return db_expense


def update_expense(
    db: Session, expense_id: int, expense_in: ExpenseUpdate
) -> Optional[Expense]:
    """Partially update an expense — only fields explicitly set are written."""
    db_expense = get_expense(db, expense_id)
    if not db_expense:
        return None

    updates = expense_in.dict(exclude_unset=True)
    for field, value in updates.items():
        setattr(db_expense, field, value)

    db.commit()
    db.refresh(db_expense)
    return db_expense


def delete_expense(db: Session, expense_id: int) -> bool:
    """Delete an expense and best-effort drop the image file. Returns False if not found."""
    db_expense = get_expense(db, expense_id)
    if not db_expense:
        return False

    if db_expense.image_path and os.path.exists(db_expense.image_path):
        try:
            os.remove(db_expense.image_path)
        except OSError:
            pass

    db.delete(db_expense)
    db.commit()
    return True


def list_expense_items(db: Session, expense_id: int) -> Optional[List[LineItem]]:
    """Return the line items for an expense in order, or None if expense missing."""
    expense = get_expense(db, expense_id)
    if not expense:
        return None
    return list(expense.items)
