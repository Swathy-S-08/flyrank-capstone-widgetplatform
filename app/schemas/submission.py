import uuid

from pydantic import BaseModel, Field


class SubmissionIn(BaseModel):
    widget_id: str = Field(min_length=1, max_length=16)
    data: dict[str, str]
    idempotency_key: str | None = Field(default=None, max_length=100)
    website: str = ""  # honeypot, always empty for real visitors


class SubmissionOut(BaseModel):
    id: uuid.UUID
