import uuid

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.auth import get_current_owner
from app.core.database import get_db
from app.schemas.dashboard import Stats, SubmissionPage
from app.services import dashboard_service

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("/submissions", response_model=SubmissionPage)
def list_submissions(
    widget_id: str | None = Query(default=None, max_length=16),
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
    owner_id: uuid.UUID = Depends(get_current_owner),
):
    return dashboard_service.list_submissions(db, owner_id, widget_id, limit, offset)


@router.get("/stats", response_model=Stats)
def stats(
    days: int = Query(default=30, ge=1, le=365),
    db: Session = Depends(get_db),
    owner_id: uuid.UUID = Depends(get_current_owner),
):
    return dashboard_service.stats(db, owner_id, days)
