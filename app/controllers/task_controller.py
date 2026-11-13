from typing import Annotated

from fastapi import APIRouter, Depends, Path, Query, Response, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.repositories.task_repository import TaskRepository
from app.schemas.task_schema import TaskCreate, TaskResponse, TaskStatsResponse, TaskUpdate
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
    completed: Annotated[bool | None, Query(
        description="Filtra pela situação: true para concluídas, false para pendentes; omitido lista todas.",
    )] = None,
    search: Annotated[str | None, Query(
        description="Texto parcial no título ou descrição, sem distinguir maiúsculas. "
                    "Espaços nas extremidades são removidos; texto vazio não filtra. % e _ são literais.",
    )] = None,
):
    return service.list_tasks(current_user.id, completed, search)


@router.get(
    "/stats", response_model=TaskStatsResponse,
    summary="Consultar estatísticas das tarefas do usuário autenticado",
    description="Considera todas as tarefas do usuário, independentemente dos filtros da listagem.",
    responses={401: {"description": "Autenticação necessária ou token inválido."}},
)
def get_task_stats(
    current_user: Annotated[User, Depends(get_current_user)],
    service: Annotated[TaskService, Depends(get_task_service)],
):
    return service.get_stats(current_user.id)


@router.get(
    "/{id}",
    response_model=TaskResponse,
    summary="Consultar uma tarefa do usuário autenticado",
    responses={
        401: {"description": "Autenticação necessária ou token inválido."},
        404: {"description": "Tarefa não encontrada ou pertencente a outro usuário."},
    },
)
def get_task(
    task_id: Annotated[int, Path(alias="id", ge=1, le=2**63 - 1)],
    current_user: Annotated[User, Depends(get_current_user)],
    service: Annotated[TaskService, Depends(get_task_service)],
):
    return service.get_task(current_user.id, task_id)


@router.put(
    "/{id}", response_model=TaskResponse,
    summary="Editar título e descrição de uma tarefa",
    responses={401: {"description": "Autenticação necessária."},
               404: {"description": "Tarefa não encontrada."}},
)
def update_task(
    task_id: Annotated[int, Path(alias="id", ge=1, le=2**63 - 1)],
    data: TaskUpdate,
    current_user: Annotated[User, Depends(get_current_user)],
    service: Annotated[TaskService, Depends(get_task_service)],
):
    return service.update_task(current_user.id, task_id, data)


@router.patch(
    "/{id}/complete", response_model=TaskResponse,
    summary="Concluir uma tarefa pendente",
    responses={400: {"description": "A tarefa já está concluída."},
               401: {"description": "Autenticação necessária."},
               404: {"description": "Tarefa não encontrada."}},
)
def complete_task(
    task_id: Annotated[int, Path(alias="id", ge=1, le=2**63 - 1)],
    current_user: Annotated[User, Depends(get_current_user)],
    service: Annotated[TaskService, Depends(get_task_service)],
):
    return service.complete_task(current_user.id, task_id)


@router.delete(
    "/{id}", status_code=status.HTTP_204_NO_CONTENT, response_class=Response,
    summary="Excluir uma tarefa",
    responses={401: {"description": "Autenticação necessária."},
               404: {"description": "Tarefa não encontrada."}},
)
def delete_task(
    task_id: Annotated[int, Path(alias="id", ge=1, le=2**63 - 1)],
    current_user: Annotated[User, Depends(get_current_user)],
    service: Annotated[TaskService, Depends(get_task_service)],
) -> Response:
    service.delete_task(current_user.id, task_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
