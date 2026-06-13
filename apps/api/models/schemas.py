"""
Pydantic schemas for the Pluto API request/response payloads.

These are pure data classes — no DB access, no business logic. Routers
and services use them to validate input and shape output.
"""

from __future__ import annotations

from datetime import date as date_type

from pydantic import BaseModel, Field


class LineItemIn(BaseModel):
    name: str
    price: float
    quantity: int = 1
    category: str | None = None

    class Config:
        from_attributes: bool = True


class LineItemOut(BaseModel):
    id: int
    order_index: int
    name: str
    price: float
    quantity: int
    category: str | None = None

    class Config:
        from_attributes: bool = True


class ExpenseOut(BaseModel):
    id: int
    date: date_type
    time: str | None = None
    amount: float
    currency: str
    subtotal: float | None = None
    tax: float | None = None
    tip: float | None = None
    discount: float | None = None
    payment_method: str | None = None
    card_type: str | None = None
    card_last4: str | None = None
    cashier: str | None = None
    transaction_id: str | None = None
    reference_id: str | None = None
    auth_id: str | None = None
    address: str | None = None
    phone: str | None = None
    email: str | None = None
    category: str
    merchant: str
    merchant_id: int | None = None
    notes: str
    image_path: str
    raw_text: str | None = None
    created_at: str
    updated_at: str
    synced_at: str | None = None
    line_items: list[object] = Field(default_factory=list)

    class Config:
        from_attributes: bool = True


class CategoryOut(BaseModel):
    id: int
    name: str
    icon: str

    class Config:
        from_attributes: bool = True


class MerchantOut(BaseModel):
    id: int
    name: str
    address: str | None = None
    phone: str | None = None
    email: str | None = None
    first_seen: date_type | None = None
    last_seen: date_type | None = None
    visit_count: int

    class Config:
        from_attributes: bool = True


class ScanOut(BaseModel):
    image_path: str
    extracted: dict[str, object]
    errors: list[str] = Field(default_factory=list)
    needs_review: list[str] = Field(default_factory=list)


class CategoryBreakdown(BaseModel):
    category: str
    total: float
    count: int


class StatsOut(BaseModel):
    total: float
    count: int
    by_category: list[CategoryBreakdown] = Field(default_factory=list)
    filters: dict[str, object] = Field(default_factory=dict)


class SyncRequest(BaseModel):
    folder: str
    direction: str = Field("push", pattern="^(push|pull|auto)$")


class SyncResult(BaseModel):
    action: str
    folder: str
    detail: str
