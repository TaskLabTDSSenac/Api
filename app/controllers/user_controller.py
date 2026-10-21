from typing import Annotated

from fastapi import APIRouter, Depends

from app.models.user import User
from app.schemas.user_schema import UserResponse
from app.security.dependencies import get_current_user


router = APIRouter(prefix="/users", tags=["Usuários"])


@router.get("/me", response_model=UserResponse)
def me(user: Annotated[User, Depends(get_current_user)]):
    return user
