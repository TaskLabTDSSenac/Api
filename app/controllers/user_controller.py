from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.schemas.user_schema import PasswordChangeRequest, UserResponse
from app.security.dependencies import get_current_user
from app.services.user_service import UserService


router = APIRouter(prefix="/users", tags=["Usuários"])


def get_user_service(session: Annotated[Session, Depends(get_db)]) -> UserService:
    return UserService(UserRepository(session))


@router.get("/me", response_model=UserResponse)
def me(user: Annotated[User, Depends(get_current_user)]):
    return user


@router.patch(
    "/me/password", response_model=dict[str, str],
    summary="Alterar a senha do usuário autenticado",
    responses={
        400: {"description": "Senha atual incorreta ou nova senha igual à atual."},
        401: {"description": "Autenticação necessária ou token inválido."},
    },
)
def change_password(
    data: PasswordChangeRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    service: Annotated[UserService, Depends(get_user_service)],
) -> dict[str, str]:
    service.change_password(current_user, data)
    return {"detail": "Senha alterada com sucesso."}
