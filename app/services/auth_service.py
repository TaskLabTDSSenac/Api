import sqlite3

from sqlalchemy.exc import IntegrityError

from app.exceptions import EmailAlreadyExistsError
from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.schemas.user_schema import UserCreate
from app.security.password import hash_password


class AuthService:
    def __init__(self, repository: UserRepository):
        self.repository = repository

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
