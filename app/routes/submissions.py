from fastapi import APIRouter, Depends, Request, Response
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.submission import SubmissionIn, SubmissionOut
from app.services import submission_service

router = APIRouter(prefix="/submissions", tags=["submissions"])


@router.post("", response_model=SubmissionOut, status_code=201)
def create_submission(
    body: SubmissionIn,
    request: Request,
    response: Response,
    db: Session = Depends(get_db),
):
    ip = request.client.host if request.client else None
    submission_id, created = submission_service.create_submission(db, body, ip)
    if not created:
        response.status_code = 200  # idempotent replay
    return {"id": submission_id}
