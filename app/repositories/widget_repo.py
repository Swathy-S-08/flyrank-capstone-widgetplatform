import secrets
import string
import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Widget

_ALPHABET = string.ascii_lowercase + string.digits


def new_widget_id() -> str:
    return "".join(secrets.choice(_ALPHABET) for _ in range(10))


def create(db: Session, owner_id: uuid.UUID, values: dict) -> Widget:
    widget = Widget(id=new_widget_id(), owner_id=owner_id, **values)
    db.add(widget)
    db.commit()
    db.refresh(widget)
    return widget


def list_for_owner(db: Session, owner_id: uuid.UUID) -> list[Widget]:
    stmt = (
        select(Widget)
        .where(Widget.owner_id == owner_id)
        .order_by(Widget.created_at.desc())
    )
    return list(db.scalars(stmt))


def get_for_owner(db: Session, widget_id: str, owner_id: uuid.UUID) -> Widget | None:
    stmt = select(Widget).where(Widget.id == widget_id, Widget.owner_id == owner_id)
    return db.scalar(stmt)


def save(db: Session, widget: Widget) -> Widget:
    db.commit()
    db.refresh(widget)
    return widget


def delete(db: Session, widget: Widget) -> None:
    db.delete(widget)
    db.commit()


def get_public(db: Session, widget_id: str) -> Widget | None:
    return db.scalar(select(Widget).where(Widget.id == widget_id))
