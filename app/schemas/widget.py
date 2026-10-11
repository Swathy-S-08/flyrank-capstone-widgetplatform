from datetime import datetime
from typing import Literal

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    computed_field,
    field_validator,
)

from app.core.config import settings


class FieldDef(BaseModel):
    name: str = Field(pattern=r"^[a-z][a-z0-9_]{0,31}$")
    label: str = Field(min_length=1, max_length=100)
    type: Literal["text", "email", "textarea"] = "text"
    required: bool = False

    @field_validator("name")
    @classmethod
    def not_reserved(cls, v: str) -> str:
        if v == "website":
            raise ValueError("'website' is reserved for the honeypot")
        return v


class WidgetIn(BaseModel):
    type: Literal["contact_form"] = "contact_form"
    title: str = Field(min_length=1, max_length=200)
    description: str | None = Field(default=None, max_length=1000)
    fields: list[FieldDef] = Field(min_length=1, max_length=10)
    button_text: str = Field(default="Submit", min_length=1, max_length=64)
    is_active: bool = True


class WidgetOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    type: str
    title: str
    description: str | None
    fields: list[FieldDef]
    button_text: str
    is_active: bool
    config_version: int
    created_at: datetime
    updated_at: datetime

    @computed_field
    @property
    def embed_snippet(self) -> str:
        return f'<script src="{settings.public_base_url}/widget.js?id={self.id}"></script>'
