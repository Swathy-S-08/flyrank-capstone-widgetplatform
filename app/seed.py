from datetime import datetime, timedelta, timezone

from sqlalchemy import select

from app.core.auth import DEMO_OWNERS
from app.core.database import SessionLocal
from app.models import Submission, Widget

FIELDS = [
    {"name": "email", "label": "Email", "type": "email", "required": True},
    {"name": "message", "label": "Message", "type": "textarea", "required": True},
]

# (email, message, country, city, provider, days_ago)
SAMPLES = [
    ("alice@example.com", "Interested in a demo", "India", "Kochi", "ip-api.com", 0),
    ("bob@example.com", "Pricing question", "Germany", "Berlin", "ip-api.com", 1),
    ("carol@example.com", "Partnership inquiry", "United States", "Austin", "ipapi.co", 1),
    ("dan@example.com", "Support request", None, None, None, 2),
    ("erin@example.com", "Feature suggestion", "India", "Chennai", "ip-api.com", 3),
    ("frank@example.com", "Hello there", "Germany", "Munich", "ipapi.co", 5),
]


def seed() -> None:
    owner1 = DEMO_OWNERS["demo-owner-1"]
    owner2 = DEMO_OWNERS["demo-owner-2"]

    with SessionLocal() as db:
        if db.get(Widget, "demo-contact") is None:
            db.add(
                Widget(
                    id="demo-contact",
                    owner_id=owner1,
                    title="Contact us (demo)",
                    description="Demo widget for evaluation",
                    fields=FIELDS,
                    button_text="Send",
                )
            )
        if db.get(Widget, "demo-other") is None:
            db.add(
                Widget(
                    id="demo-other",
                    owner_id=owner2,
                    title="Other tenant widget",
                    description="Belongs to demo-owner-2",
                    fields=FIELDS,
                    button_text="Send",
                )
            )
        db.commit()

        now = datetime.now(timezone.utc)
        added = 0
        for i, (email, msg, country, city, provider, days_ago) in enumerate(SAMPLES, 1):
            key = f"seed-{i}"
            exists = db.scalar(
                select(Submission.id).where(
                    Submission.widget_id == "demo-contact",
                    Submission.idempotency_key == key,
                )
            )
            if exists:
                continue
            db.add(
                Submission(
                    widget_id="demo-contact",
                    owner_id=owner1,
                    data={"email": email, "message": msg},
                    country=country,
                    city=city,
                    geo_provider=provider,
                    idempotency_key=key,
                    notification_status="sent",
                    created_at=now - timedelta(days=days_ago),
                )
            )
            added += 1
        db.commit()

    print(f"Seed complete: widgets demo-contact and demo-other, {added} new submissions.")


if __name__ == "__main__":
    seed()
