from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.repositories.user_repository import UserRepository
from app.schemas.user_schema import UserCreate, UserResponse
from app.schemas.auth_schema import LoginRequest, TokenResponse
from app.services.auth_service import AuthService


router = APIRouter(prefix="/auth", tags=["Autenticação"])


def get_auth_service(session: Annotated[Session, Depends(get_db)]) -> AuthService:
    return AuthService(UserRepository(session))


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(data: UserCreate, service: Annotated[AuthService, Depends(get_auth_service)]):
    return service.register(data)


@router.post("/login", response_model=TokenResponse)
def login(data: LoginRequest, service: Annotated[AuthService, Depends(get_auth_service)]):
    return service.login(data)
