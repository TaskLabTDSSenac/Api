from typing import Literal

from pydantic import BaseModel, Field

from app.schemas.user_schema import EmailRequest


class LoginRequest(EmailRequest):
    password: str = Field(min_length=1, max_length=128, repr=False)


class TokenResponse(BaseModel):
    access_token: str
    token_type: Literal["bearer"] = "bearer"
