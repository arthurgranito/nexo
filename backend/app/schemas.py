from datetime import datetime
from typing import Literal
from pydantic import BaseModel, ConfigDict, Field, field_validator

class Input(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

class SourceCreate(Input):
    name: str = Field(min_length=2, max_length=120)
    kind: Literal["csv", "xlsx", "google_sheets", "postgres", "mysql"]

class SourceRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    name: str
    kind: str
    status: str
    created_at: datetime

class Question(Input):
    text: str = Field(min_length=3, max_length=4000)

class CorrectionCreate(Input):
    message_id: str = Field(min_length=36, max_length=36)
    reason: str = Field(min_length=5, max_length=2000)
    proposed_rule: str = Field(min_length=5, max_length=2000)

class DashboardCreate(Input):
    name: str = Field(min_length=2, max_length=120)
    spec: dict = Field(default_factory=dict)

    @field_validator("spec")
    @classmethod
    def valid_chart(cls, value):
        if set(value) - {"type", "query_run_id", "x", "y"}:
            raise ValueError("Apenas type, query_run_id, x e y são permitidos")
        if value.get("type", "table") not in {"table", "bar", "line", "number"}:
            raise ValueError("Visualização inválida")
        return value
