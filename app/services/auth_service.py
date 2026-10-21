import sqlite3
import secrets

from sqlalchemy.exc import IntegrityError

from app.exceptions import EmailAlreadyExistsError, InvalidCredentialsError
from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.schemas.user_schema import UserCreate
from app.schemas.auth_schema import LoginRequest, TokenResponse
from app.security.jwt import create_access_token
from app.security.password import hash_password, verify_password


# Preparado uma única vez por processo, para a verificação de usuários ausentes.
DUMMY_PASSWORD_HASH = hash_password(secrets.token_urlsafe(32))


class AuthService:
    def __init__(self, repository: UserRepository):
        self.repository = repository

    def login(self, data: LoginRequest) -> TokenResponse:
        user = self.repository.get_by_email(data.email)
        password_hash = user.password_hash if user is not None else DUMMY_PASSWORD_HASH
        valid_password = verify_password(data.password, password_hash)
        if user is None or not valid_password:
            raise InvalidCredentialsError()
        return TokenResponse(access_token=create_access_token(user.id))

    def register(self, data: UserCreate) -> User:
        if self.repository.get_by_email(data.email) is not None:
            raise EmailAlreadyExistsError()

        password_hash = hash_password(data.password)
        try:
            return self.repository.create(data.name, data.email, password_hash)
        except IntegrityError as error:
            # A restrição única também protege contra cadastros simultâneos.
            original = error.orig
            if (
                isinstance(original, sqlite3.IntegrityError)
                and original.sqlite_errorcode == sqlite3.SQLITE_CONSTRAINT_UNIQUE
                and str(original) == "UNIQUE constraint failed: users.email"
            ):
                raise EmailAlreadyExistsError() from error
            raise
