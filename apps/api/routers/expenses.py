"""
Expense CRUD + line items.

Endpoints:
- GET    /expenses               — list with optional category/month/year filters
- POST   /expenses               — create (with nested line items)
- GET    /expenses/{id}/items    — list line items for one expense
- PUT    /expenses/{id}          — partial update
- DELETE /expenses/{id}          — delete (and best-effort drop the image)
"""
from __future__ import annotations

from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from core.database import get_db
from models.schemas import ExpenseCreate, ExpenseUpdate
from services import expense_service

router = APIRouter(tags=["expenses"])


@router.get("/expenses", response_model=List[dict])
def list_expenses(
    category: Optional[str] = Query(None, description="Filter by category"),
    month: Optional[int] = Query(None, ge=1, le=12, description="Month (1-12)"),
    year: Optional[int] = Query(None, ge=1970, le=9999, description="4-digit year"),
    limit: int = Query(50, ge=1, le=500),
    db: Session = Depends(get_db),
):
    rows = expense_service.list_expenses(db, category, month, year, limit)
    return [expense_service.expense_to_dict(e) for e in rows]


@router.post("/expenses", response_model=dict)
def create_expense(expense_in: ExpenseCreate, db: Session = Depends(get_db)):
    db_expense = expense_service.create_expense(db, expense_in)
    return expense_service.expense_to_dict(db_expense)


@router.get("/expenses/{expense_id}/items")
def list_expense_items(expense_id: int, db: Session = Depends(get_db)):
    items = expense_service.list_expense_items(db, expense_id)
    if items is None:
        raise HTTPException(status_code=404, detail="Expense not found")
    return [
        {
            "id": li.id,
            "order_index": li.order_index,
            "name": li.name,
            "price": li.price,
            "quantity": li.quantity,
            "category": li.category,
        }
        for li in items
    ]


@router.put("/expenses/{expense_id}", response_model=dict)
def update_expense(
    expense_id: int, expense_in: ExpenseUpdate, db: Session = Depends(get_db),
):
    db_expense = expense_service.update_expense(db, expense_id, expense_in)
    if not db_expense:
        raise HTTPException(status_code=404, detail="Expense not found")
    return expense_service.expense_to_dict(db_expense)


@router.delete("/expenses/{expense_id}")
def delete_expense(expense_id: int, db: Session = Depends(get_db)):
    ok = expense_service.delete_expense(db, expense_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Expense not found")
    return {"detail": "Expense deleted"}
