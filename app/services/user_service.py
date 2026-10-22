from app.exceptions import IncorrectCurrentPasswordError, SamePasswordError
from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.schemas.user_schema import PasswordChangeRequest
from app.security.password import hash_password, verify_password


class UserService:
    def __init__(self, repository: UserRepository):
        self.repository = repository

    def change_password(self, user: User, data: PasswordChangeRequest) -> None:
        if not verify_password(data.current_password, user.password_hash):
            raise IncorrectCurrentPasswordError()
        if data.new_password == data.current_password:
            raise SamePasswordError()
        self.repository.update_password(user, hash_password(data.new_password))
