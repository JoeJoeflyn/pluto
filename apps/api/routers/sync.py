"""
Local SQLite file sync — push/pull the database to a shared folder.
"""
from __future__ import annotations

import os

from fastapi import APIRouter, HTTPException

from models.schemas import SyncRequest, SyncResult
from services import sync_service

router = APIRouter(tags=["sync"])


_DB_PATH = os.path.abspath("./expenses.db")


@router.post("/sync", response_model=SyncResult)
def sync(req: SyncRequest):
    try:
        result = sync_service.sync_database(req.folder, req.direction, _DB_PATH)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    return SyncResult(**result)
