from fastapi import APIRouter, BackgroundTasks, Depends, Request, Response
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.rate_limit import rate_limit_submissions
from app.schemas.submission import SubmissionIn, SubmissionOut
from app.services import notifier, submission_service

router = APIRouter(prefix="/submissions", tags=["submissions"])


@router.post(
    "",
    response_model=SubmissionOut,
    status_code=201,
    dependencies=[Depends(rate_limit_submissions)],
)
def create_submission(
    body: SubmissionIn,
    request: Request,
    response: Response,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):
    ip = request.client.host if request.client else None
    submission_id, created = submission_service.create_submission(db, body, ip)
    if created:
        background_tasks.add_task(notifier.send_confirmation, submission_id)
    else:
        response.status_code = 200  # idempotent replay: no second email
    return {"id": submission_id}
