from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.models.user import User, utc_now


class UserRepository:
    def __init__(self, session: Session):
        self.session = session

    def get_by_email(self, email: str) -> User | None:
        return self.session.scalar(select(User).where(User.email == email))

    def get_by_id(self, user_id: int) -> User | None:
        return self.session.get(User, user_id)

    def update_password(self, user: User, password_hash: str) -> None:
        try:
            user.password_hash = password_hash
            user.updated_at = utc_now()
            self.session.commit()
        except SQLAlchemyError:
            self.session.rollback()
            raise

    def create(self, name: str, email: str, password_hash: str) -> User:
        user = User(name=name, email=email, password_hash=password_hash)
        try:
            self.session.add(user)
            self.session.commit()
            self.session.refresh(user)
        except SQLAlchemyError:
            self.session.rollback()
            raise
        return user
