from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.repositories.task_repository import TaskRepository
from app.schemas.task_schema import TaskCreate, TaskResponse
from app.security.dependencies import get_current_user
from app.services.task_service import TaskService


router = APIRouter(prefix="/tasks", tags=["Tarefas"])


def get_task_service(session: Annotated[Session, Depends(get_db)]) -> TaskService:
    return TaskService(TaskRepository(session))


@router.post("", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
def create_task(
    data: TaskCreate,
    current_user: Annotated[User, Depends(get_current_user)],
    service: Annotated[TaskService, Depends(get_task_service)],
):
    return service.create_task(current_user.id, data)


@router.get("", response_model=list[TaskResponse])
def list_tasks(
    current_user: Annotated[User, Depends(get_current_user)],
    service: Annotated[TaskService, Depends(get_task_service)],
):
    return service.list_tasks(current_user.id)
