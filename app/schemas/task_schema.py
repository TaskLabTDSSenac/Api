from datetime import datetime, timezone
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field, StringConstraints, field_validator


class TaskCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    title: Annotated[str, StringConstraints(strip_whitespace=True, min_length=3, max_length=150)]
    description: str | None = Field(default=None, max_length=500)


class TaskResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    description: str | None
    completed: bool
    created_at: datetime
    updated_at: datetime

    @field_validator("created_at", "updated_at")
    @classmethod
    def timestamps_in_utc(cls, value: datetime) -> datetime:
        # O SQLite devolve sem fuso os timestamps que gravamos em UTC.
        if value.tzinfo is None:
            return value.replace(tzinfo=timezone.utc)
        return value.astimezone(timezone.utc)
