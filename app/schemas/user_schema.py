from typing import Annotated

from pydantic import BaseModel, ConfigDict, EmailStr, Field, StringConstraints, field_validator


class EmailRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    email: EmailStr = Field(max_length=255)

    @field_validator("email", mode="before")
    @classmethod
    def strip_email(cls, value):
        return value.strip() if isinstance(value, str) else value

    @field_validator("email")
    @classmethod
    def normalize_email(cls, value: str) -> str:
        return value.lower()


class UserCreate(EmailRequest):
    name: Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=150)]
    password: str = Field(min_length=8, max_length=128, repr=False)


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    email: str


class PasswordChangeRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    current_password: str = Field(min_length=1, max_length=128, repr=False)
    new_password: str = Field(min_length=8, max_length=128, repr=False)
