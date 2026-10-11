import uuid

from fastapi import APIRouter, Depends, Response
from sqlalchemy.orm import Session

from app.core.auth import get_current_owner
from app.core.database import get_db
from app.schemas.widget import WidgetIn, WidgetOut
from app.services import widget_service

router = APIRouter(prefix="/widgets", tags=["widgets"])


@router.post("", response_model=WidgetOut, status_code=201)
def create_widget(
    body: WidgetIn,
    db: Session = Depends(get_db),
    owner_id: uuid.UUID = Depends(get_current_owner),
):
    return widget_service.create_widget(db, owner_id, body)


@router.get("", response_model=list[WidgetOut])
def list_widgets(
    db: Session = Depends(get_db),
    owner_id: uuid.UUID = Depends(get_current_owner),
):
    return widget_service.list_widgets(db, owner_id)


@router.get("/{widget_id}", response_model=WidgetOut)
def get_widget(
    widget_id: str,
    db: Session = Depends(get_db),
    owner_id: uuid.UUID = Depends(get_current_owner),
):
    return widget_service.get_widget(db, owner_id, widget_id)


@router.put("/{widget_id}", response_model=WidgetOut)
def update_widget(
    widget_id: str,
    body: WidgetIn,
    db: Session = Depends(get_db),
    owner_id: uuid.UUID = Depends(get_current_owner),
):
    return widget_service.update_widget(db, owner_id, widget_id, body)


@router.delete("/{widget_id}", status_code=204)
def delete_widget(
    widget_id: str,
    db: Session = Depends(get_db),
    owner_id: uuid.UUID = Depends(get_current_owner),
):
    widget_service.delete_widget(db, owner_id, widget_id)
    return Response(status_code=204)
