import uuid

from sqlalchemy.orm import Session

from app.core.errors import NotFoundError
from app.models import Widget
from app.repositories import widget_repo
from app.schemas.widget import WidgetIn


def create_widget(db: Session, owner_id: uuid.UUID, data: WidgetIn) -> Widget:
    return widget_repo.create(db, owner_id, data.model_dump())


def list_widgets(db: Session, owner_id: uuid.UUID) -> list[Widget]:
    return widget_repo.list_for_owner(db, owner_id)


def get_widget(db: Session, owner_id: uuid.UUID, widget_id: str) -> Widget:
    widget = widget_repo.get_for_owner(db, widget_id, owner_id)
    if widget is None:
        raise NotFoundError("Widget not found")
    return widget


def update_widget(
    db: Session, owner_id: uuid.UUID, widget_id: str, data: WidgetIn
) -> Widget:
    widget = get_widget(db, owner_id, widget_id)
    for key, value in data.model_dump().items():
        setattr(widget, key, value)
    widget.config_version += 1
    return widget_repo.save(db, widget)


def delete_widget(db: Session, owner_id: uuid.UUID, widget_id: str) -> None:
    widget = get_widget(db, owner_id, widget_id)
    widget_repo.delete(db, widget)
