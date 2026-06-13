"""
Pluto API — FastAPI surface for the receipt scanner.

Layered as:
- core/      config + SQLAlchemy models + DB session
- models/    Pydantic request/response schemas
- services/  business logic (AI extraction, expense/merchant/category/stats/sync)
- routers/   one FastAPI router per resource

Run with:
    cd apps/api
    uvicorn main:app --reload
"""
from __future__ import annotations

import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from core.config import RECEIPTS_DIR
from core.database import init_db
from routers import categories, expenses, health, merchants, scan, stats, sync

os.makedirs(RECEIPTS_DIR, exist_ok=True)

app = FastAPI(title="Pluto API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def _startup():
    init_db()


app.include_router(health.router)
app.include_router(scan.router)
app.include_router(expenses.router)
app.include_router(merchants.router)
app.include_router(categories.router)
app.include_router(stats.router)
app.include_router(sync.router)

app.mount("/receipts", StaticFiles(directory=RECEIPTS_DIR), name="receipts")
