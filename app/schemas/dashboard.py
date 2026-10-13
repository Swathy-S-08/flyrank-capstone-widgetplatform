import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class SubmissionRow(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    widget_id: str
    data: dict
    country: str | None
    city: str | None
    geo_provider: str | None
    notification_status: str
    created_at: datetime


class SubmissionPage(BaseModel):
    items: list[SubmissionRow]
    total: int
    limit: int
    offset: int


class WidgetCount(BaseModel):
    widget_id: str
    title: str
    count: int


class DayCount(BaseModel):
    date: str
    count: int


class CountryCount(BaseModel):
    country: str
    count: int


class Stats(BaseModel):
    total: int
    per_widget: list[WidgetCount]
    per_day: list[DayCount]
    per_country: list[CountryCount]
