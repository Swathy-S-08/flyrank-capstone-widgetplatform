import uuid
from datetime import datetime

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models import Submission, Widget


def list_submissions(
    db: Session, owner_id: uuid.UUID, widget_id: str | None, limit: int, offset: int
) -> tuple[list[Submission], int]:
    stmt = select(Submission).where(Submission.owner_id == owner_id)
    if widget_id:
        stmt = stmt.where(Submission.widget_id == widget_id)
    total = db.scalar(select(func.count()).select_from(stmt.subquery())) or 0
    rows = db.scalars(
        stmt.order_by(Submission.created_at.desc()).limit(limit).offset(offset)
    ).all()
    return list(rows), total


def total_count(db: Session, owner_id: uuid.UUID) -> int:
    stmt = select(func.count()).select_from(Submission).where(
        Submission.owner_id == owner_id
    )
    return db.scalar(stmt) or 0


def count_per_widget(db: Session, owner_id: uuid.UUID) -> list[tuple]:
    count = func.count(Submission.id)
    stmt = (
        select(Widget.id, Widget.title, count)
        .join(Submission, Submission.widget_id == Widget.id, isouter=True)
        .where(Widget.owner_id == owner_id)
        .group_by(Widget.id, Widget.title)
        .order_by(count.desc(), Widget.title)
    )
    return list(db.execute(stmt).all())


def count_per_day(db: Session, owner_id: uuid.UUID, since: datetime) -> list[tuple]:
    day = func.date_trunc("day", Submission.created_at)
    stmt = (
        select(day, func.count(Submission.id))
        .where(Submission.owner_id == owner_id, Submission.created_at >= since)
        .group_by(day)
        .order_by(day)
    )
    return list(db.execute(stmt).all())


def count_per_country(db: Session, owner_id: uuid.UUID) -> list[tuple]:
    count = func.count(Submission.id)
    stmt = (
        select(Submission.country, count)
        .where(Submission.owner_id == owner_id)
        .group_by(Submission.country)
        .order_by(count.desc())
    )
    return list(db.execute(stmt).all())
