from typing import Annotated

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.database import get_db
from app.exceptions import AuthenticationRequiredError
from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.security.jwt import decode_access_token


bearer = HTTPBearer(auto_error=False)


def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer)],
    session: Annotated[Session, Depends(get_db)],
) -> User:
    if credentials is None or credentials.scheme.lower() != "bearer":
        raise AuthenticationRequiredError()
    user_id = decode_access_token(credentials.credentials)
    user = UserRepository(session).get_by_id(user_id)
    if user is None:
        raise AuthenticationRequiredError()
    return user
