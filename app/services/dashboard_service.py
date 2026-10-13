import uuid
from datetime import datetime, timedelta, timezone

from sqlalchemy.orm import Session

from app.repositories import dashboard_repo


def list_submissions(
    db: Session, owner_id: uuid.UUID, widget_id: str | None, limit: int, offset: int
) -> dict:
    rows, total = dashboard_repo.list_submissions(db, owner_id, widget_id, limit, offset)
    return {"items": rows, "total": total, "limit": limit, "offset": offset}


def stats(db: Session, owner_id: uuid.UUID, days: int) -> dict:
    since = datetime.now(timezone.utc) - timedelta(days=days)
    return {
        "total": dashboard_repo.total_count(db, owner_id),
        "per_widget": [
            {"widget_id": wid, "title": title, "count": n}
            for wid, title, n in dashboard_repo.count_per_widget(db, owner_id)
        ],
        "per_day": [
            {"date": day.date().isoformat(), "count": n}
            for day, n in dashboard_repo.count_per_day(db, owner_id, since)
        ],
        "per_country": [
            {"country": country or "Unknown", "count": n}
            for country, n in dashboard_repo.count_per_country(db, owner_id)
        ],
    }
