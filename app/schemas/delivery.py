from pydantic import BaseModel, ConfigDict

from app.schemas.widget import FieldDef


class WidgetConfigOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    type: str
    title: str
    description: str | None
    fields: list[FieldDef]
    button_text: str
    config_version: int
