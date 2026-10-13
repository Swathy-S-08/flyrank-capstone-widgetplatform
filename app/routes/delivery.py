from pathlib import Path

from fastapi import APIRouter, Depends, Response
from fastapi.responses import FileResponse, RedirectResponse
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.errors import NotFoundError
from app.repositories import widget_repo
from app.schemas.delivery import WidgetConfigOut

router = APIRouter(tags=["delivery"])

BUNDLE = Path(__file__).resolve().parent.parent / "static" / "widget.v1.js"
IMMUTABLE = "public, max-age=31536000, immutable"


@router.get("/widgets/{widget_id}/config", response_model=WidgetConfigOut)
def widget_config(widget_id: str, response: Response, db: Session = Depends(get_db)):
    widget = widget_repo.get_public(db, widget_id)
    if widget is None or not widget.is_active:
        raise NotFoundError("Widget not found")
    response.headers["Cache-Control"] = "public, max-age=60"
    return widget


@router.get("/widget.v1.js")
def widget_bundle():
    return FileResponse(
        BUNDLE,
        media_type="application/javascript",
        headers={"Cache-Control": IMMUTABLE},
    )


@router.get("/widget.js")
def widget_loader():
    return RedirectResponse(
        url="/widget.v1.js",
        status_code=302,
        headers={"Cache-Control": "public, max-age=300"},
    )
