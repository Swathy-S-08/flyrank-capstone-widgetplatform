import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Submission


def get_by_idempotency_key(
    db: Session, widget_id: str, key: str
) -> Submission | None:
    stmt = select(Submission).where(
        Submission.widget_id == widget_id, Submission.idempotency_key == key
    )
    return db.scalar(stmt)


def create(db: Session, values: dict) -> Submission:
    submission = Submission(**values)
    db.add(submission)
    db.commit()
    db.refresh(submission)
    return submission
