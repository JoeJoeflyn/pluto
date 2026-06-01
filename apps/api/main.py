"""
Pluto API — FastAPI surface for the receipt scanner.

Implements the endpoints described in
docs/superpowers/specs/2026-06-01-receipt-scanner-design.md:
- /health
- /scan           (POST) — upload an image, get an AI extraction
- /expenses       (GET, POST)
- /expenses/{id}  (PUT, DELETE)
- /categories     (GET)
- /stats          (GET) — spending totals, by month/year/category
- /sync           (POST) — push or pull the SQLite file to a folder
"""
from __future__ import annotations

import os
import shutil
import uuid
from datetime import date as date_type
from typing import List, Optional

from fastapi import Depends, FastAPI, File, HTTPException, Query, UploadFile
from pydantic import BaseModel, Field
from sqlalchemy import extract, func
from sqlalchemy.orm import Session

from .ai_service import extract_receipt_data
from .database import Category, Expense, SessionLocal, init_db


# ---------------------------------------------------------------------------
# App + setup
# ---------------------------------------------------------------------------

app = FastAPI(title="Pluto API")

# Receipts live on disk so future requests can serve the original image
# back. CWD-relative is fine for a local-first tool; the CLI and web app
# run from the project root.
RECEIPTS_DIR = "receipts"
os.makedirs(RECEIPTS_DIR, exist_ok=True)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.on_event("startup")
def startup_event():
    init_db()


# ---------------------------------------------------------------------------
# Schemas
# ---------------------------------------------------------------------------


class ExpenseCreate(BaseModel):
    date: date_type
    amount: float
    currency: str = "USD"
    category: str
    merchant: str
    notes: str = ""
    image_path: str = ""


class ExpenseUpdate(BaseModel):
    """All fields optional — only those provided will be updated."""

    amount: Optional[float] = None
    category: Optional[str] = None
    merchant: Optional[str] = None
    notes: Optional[str] = None
    date: Optional[date_type] = None
    currency: Optional[str] = None


class ExpenseOut(BaseModel):
    id: int
    date: date_type
    amount: float
    currency: str
    category: str
    merchant: str
    notes: str
    image_path: str
    created_at: str
    updated_at: str
    synced_at: Optional[str] = None

    class Config:
        orm_mode = True


class CategoryOut(BaseModel):
    id: int
    name: str
    icon: str

    class Config:
        orm_mode = True


class ScanOut(BaseModel):
    image_path: str
    extracted: dict
    errors: List[str] = Field(default_factory=list)
    needs_review: List[str] = Field(default_factory=list)


class CategoryBreakdown(BaseModel):
    category: str
    total: float
    count: int


class StatsOut(BaseModel):
    total: float
    count: int
    by_category: List[CategoryBreakdown] = Field(default_factory=list)
    filters: dict = Field(default_factory=dict)


class SyncRequest(BaseModel):
    folder: str
    direction: str = Field("push", pattern="^(push|pull|auto)$")


class SyncResult(BaseModel):
    action: str
    folder: str
    detail: str


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _expense_to_dict(e: Expense) -> dict:
    return {
        "id": e.id,
        "date": e.date.isoformat() if e.date else None,
        "amount": e.amount,
        "currency": e.currency,
        "category": e.category,
        "merchant": e.merchant,
        "notes": e.notes or "",
        "image_path": e.image_path or "",
        "created_at": e.created_at.isoformat() if e.created_at else None,
        "updated_at": e.updated_at.isoformat() if e.updated_at else None,
        "synced_at": e.synced_at.isoformat() if e.synced_at else None,
    }


def _missing_fields(extracted: dict) -> List[str]:
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
    if ext not in {".jpg", ".jpeg", ".png", ".webp", ".gif", ".bmp"}:
        raise HTTPException(
            status_code=400,
            detail=(
                f"Unsupported image type '{ext}'. "
                "Allowed: jpg, jpeg, png, webp, gif, bmp."
            ),
        )
    return os.path.join(RECEIPTS_DIR, f"{uuid.uuid4()}{ext}")


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------


@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.post("/scan", response_model=ScanOut)
async def scan_receipt(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    """
    Upload a receipt image. The AI extracts fields and returns them
    *without* writing to the database — the client confirms/edits and
    POSTs to /expenses. This matches the spec's two-step data flow.
    """
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


@app.get("/expenses", response_model=List[dict])
def list_expenses(
    category: Optional[str] = Query(None, description="Filter by category"),
    month: Optional[int] = Query(None, ge=1, le=12, description="Month (1-12)"),
    year: Optional[int] = Query(None, ge=1970, le=9999, description="4-digit year"),
    limit: int = Query(50, ge=1, le=500),
    db: Session = Depends(get_db),
):
    query = db.query(Expense)
    if category:
        query = query.filter(Expense.category == category)
    if month is not None:
        query = query.filter(extract("month", Expense.date) == month)
    if year is not None:
        query = query.filter(extract("year", Expense.date) == year)
    expenses = query.order_by(Expense.date.desc(), Expense.id.desc()).limit(limit).all()
    return [_expense_to_dict(e) for e in expenses]


@app.post("/expenses", response_model=dict)
def create_expense(expense_in: ExpenseCreate, db: Session = Depends(get_db)):
    db_expense = Expense(
        date=expense_in.date,
        amount=expense_in.amount,
        currency=expense_in.currency,
        category=expense_in.category,
        merchant=expense_in.merchant,
        notes=expense_in.notes,
        image_path=expense_in.image_path,
    )
    db.add(db_expense)
    db.commit()
    db.refresh(db_expense)
    return _expense_to_dict(db_expense)


@app.put("/expenses/{expense_id}", response_model=dict)
def update_expense(
    expense_id: int,
    expense_in: ExpenseUpdate,
    db: Session = Depends(get_db),
):
    db_expense = db.query(Expense).filter(Expense.id == expense_id).first()
    if not db_expense:
        raise HTTPException(status_code=404, detail="Expense not found")

    updates = expense_in.dict(exclude_unset=True)
    if not updates:
        raise HTTPException(status_code=400, detail="No fields to update")

    for field, value in updates.items():
        setattr(db_expense, field, value)

    db.commit()
    db.refresh(db_expense)
    return _expense_to_dict(db_expense)


@app.delete("/expenses/{expense_id}")
def delete_expense(expense_id: int, db: Session = Depends(get_db)):
    db_expense = db.query(Expense).filter(Expense.id == expense_id).first()
    if not db_expense:
        raise HTTPException(status_code=404, detail="Expense not found")

    # Best-effort: drop the image too. If the file is gone, that's fine.
    if db_expense.image_path and os.path.exists(db_expense.image_path):
        try:
            os.remove(db_expense.image_path)
        except OSError:
            pass

    db.delete(db_expense)
    db.commit()
    return {"detail": "Expense deleted"}


@app.get("/categories", response_model=List[CategoryOut])
def list_categories(db: Session = Depends(get_db)):
    categories = db.query(Category).order_by(Category.id).all()
    return [CategoryOut.from_orm(c) for c in categories]


@app.get("/stats", response_model=StatsOut)
def get_stats(
    month: Optional[int] = Query(None, ge=1, le=12),
    year: Optional[int] = Query(None, ge=1970, le=9999),
    category: bool = Query(False, description="Include per-category breakdown"),
    db: Session = Depends(get_db),
):
    query = db.query(Expense)
    if month is not None:
        query = query.filter(extract("month", Expense.date) == month)
    if year is not None:
        query = query.filter(extract("year", Expense.date) == year)

    total = query.with_entities(func.coalesce(func.sum(Expense.amount), 0.0)).scalar() or 0.0
    count = query.count()

    breakdown: List[CategoryBreakdown] = []
    if category:
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
            CategoryBreakdown(category=row[0] or "Uncategorized", total=float(row[1]), count=int(row[2]))
            for row in rows
        ]

    return StatsOut(
        total=float(total),
        count=int(count),
        by_category=breakdown,
        filters={"month": month, "year": year, "category_breakdown": category},
    )


@app.post("/sync", response_model=SyncResult)
def sync_database(req: SyncRequest):
    """
    Push the local SQLite file to a shared folder, or pull the latest
    from that folder over the local copy. Matches the spec's simple
    last-write-wins sync — no conflict resolution.
    """
    folder = os.path.abspath(os.path.expanduser(req.folder))
    if not os.path.isdir(folder):
        raise HTTPException(status_code=400, detail=f"Folder not found: {folder}")

    # SQLite file lives next to the app. Resolve relative to the API dir.
    db_path = os.path.abspath("./expenses.db")
    if not os.path.exists(db_path):
        raise HTTPException(status_code=500, detail="Local database file is missing")

    target = os.path.join(folder, "expenses.db")

    if req.direction == "push":
        shutil.copy2(db_path, target)
        return SyncResult(action="push", folder=folder, detail=f"Copied to {target}")

    if req.direction == "pull":
        if not os.path.exists(target):
            raise HTTPException(status_code=404, detail=f"No database found at {target}")
        shutil.copy2(target, db_path)
        return SyncResult(action="pull", folder=folder, detail=f"Restored from {target}")

    # auto: pull if remote is newer, otherwise push.
    if os.path.exists(target) and os.path.getmtime(target) > os.path.getmtime(db_path):
        shutil.copy2(target, db_path)
        return SyncResult(action="auto-pull", folder=folder, detail="Remote was newer; pulled.")
    shutil.copy2(db_path, target)
    return SyncResult(action="auto-push", folder=folder, detail="Local was newer; pushed.")
