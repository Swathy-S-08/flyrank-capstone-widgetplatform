import logging
import time

from app.core.config import settings
from app.core.database import SessionLocal
from app.models import Submission, Widget

log = logging.getLogger("notifier")

MAX_ATTEMPTS = 3
BASE_DELAY_SECONDS = 1.0


def _send_email(to: str, subject: str) -> None:
    # Fake email: print to the console. Swap in SMTP or Mailpit later.
    if settings.notify_fail:
        raise RuntimeError("simulated email failure")
    print(f"[EMAIL] to={to} subject={subject!r}", flush=True)


def _recipient(widget: Widget, data: dict) -> str | None:
    for f in widget.fields:
        if f.get("type") == "email" and data.get(f["name"]):
            return data[f["name"]]
    return None


def _set_status(db, submission: Submission, status: str) -> None:
    submission.notification_status = status
    db.commit()


def send_confirmation(submission_id) -> None:
    """Background job. Never raises: the submission is already stored."""
    try:
        with SessionLocal() as db:
            submission = db.get(Submission, submission_id)
            if submission is None:
                return
            widget = db.get(Widget, submission.widget_id)
            to = _recipient(widget, submission.data) if widget else None
            if to is None:
                _set_status(db, submission, "skipped")
                return

            subject = f"Thanks for contacting us ({widget.title})"
            for attempt in range(1, MAX_ATTEMPTS + 1):
                try:
                    _send_email(to, subject)
                    _set_status(db, submission, "sent")
                    return
                except Exception as exc:
                    log.warning(
                        "email attempt %s/%s failed for submission %s: %s",
                        attempt, MAX_ATTEMPTS, submission_id, exc,
                    )
                    if attempt < MAX_ATTEMPTS:
                        time.sleep(BASE_DELAY_SECONDS * attempt)

            _set_status(db, submission, "failed")
            log.error(
                "ALERT: confirmation email permanently failed for submission %s",
                submission_id,
            )
    except Exception:
        log.exception("notification job crashed for submission %s", submission_id)
