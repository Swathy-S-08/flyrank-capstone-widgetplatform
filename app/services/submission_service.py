import re
import uuid

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.errors import NotFoundError, ValidationFailed
from app.repositories import submission_repo, widget_repo
from app.schemas.submission import SubmissionIn

EMAIL_RE = re.compile(r"[^@\s]+@[^@\s]+\.[^@\s]+")
MAX_LEN = {"text": 500, "email": 254, "textarea": 5000}


def _validate_data(fields: list[dict], data: dict[str, str]) -> None:
    errors: dict[str, str] = {}
    defined = {f["name"]: f for f in fields}

    for name in data:
        if name not in defined:
            errors[name] = "Unknown field"

    for name, f in defined.items():
        value = data.get(name, "").strip()
        if not value:
            if f.get("required"):
                errors[name] = "This field is required"
            continue
        if len(value) > MAX_LEN[f["type"]]:
            errors[name] = "Too long"
        elif f["type"] == "email" and not EMAIL_RE.fullmatch(value):
            errors[name] = "Invalid email address"

    if errors:
        raise ValidationFailed(errors)


def create_submission(
    db: Session, payload: SubmissionIn, ip: str | None
) -> tuple[uuid.UUID, bool]:
    widget = widget_repo.get_public(db, payload.widget_id)
    if widget is None or not widget.is_active:
        raise NotFoundError("Widget not found")

    # Honeypot: a real visitor never fills this. Pretend it worked.
    if payload.website.strip():
        return uuid.uuid4(), True

    _validate_data(widget.fields, payload.data)

    if payload.idempotency_key:
        existing = submission_repo.get_by_idempotency_key(
            db, widget.id, payload.idempotency_key
        )
        if existing:
            return existing.id, False

    values = {
        "widget_id": widget.id,
        "owner_id": widget.owner_id,
        "data": {k: v.strip() for k, v in payload.data.items()},
        "ip_address": ip,
        "idempotency_key": payload.idempotency_key,
        "notification_status": "pending",
    }
    try:
        submission = submission_repo.create(db, values)
    except IntegrityError:
        # Two identical requests raced; the unique constraint caught the loser.
        db.rollback()
        existing = submission_repo.get_by_idempotency_key(
            db, widget.id, payload.idempotency_key or ""
        )
        if existing is None:
            raise
        return existing.id, False
    return submission.id, True
