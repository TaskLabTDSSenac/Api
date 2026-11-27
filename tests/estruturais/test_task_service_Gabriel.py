"""Testes diretos do TaskService, com Repository simulado."""

import secrets
from unittest.mock import Mock

import pytest

from app.exceptions import TaskAlreadyCompletedError, TaskNotFoundError
from app.schemas.task_schema import TaskCreate, TaskUpdate


@pytest.fixture
def test_settings(monkeypatch, tmp_path):
    database = tmp_path / "testes.db"
    monkeypatch.setenv("DATABASE_URL", f"sqlite:///{database.as_posix()}")
    monkeypatch.setenv("JWT_SECRET_KEY", secrets.token_hex(32))
    monkeypatch.setenv("JWT_ACCESS_TOKEN_EXPIRE_MINUTES", "60")
    return database


@pytest.fixture
def modulo_task_service(test_settings):
    from app.services import task_service
    return task_service


def test_criar_tarefa(modulo_task_service):
    repository = Mock(spec=modulo_task_service.TaskRepository)
    task = Mock(spec=modulo_task_service.Task)
    repository.create.return_value = task
    service = modulo_task_service.TaskService(repository)
    data = TaskCreate(title="Estudar", description="Capítulo 1")

    result = service.create_task(7, data)

    assert result is task
    repository.create.assert_called_once_with(7, "Estudar", "Capítulo 1")


@pytest.mark.parametrize(
    ("completed", "search", "expected_search"),
    [(None, None, None), (True, "  urgente  ", "urgente"), (False, "   ", None)],
)
def test_listar_tarefas_normaliza_busca(
    modulo_task_service, completed, search, expected_search
):
    repository = Mock(spec=modulo_task_service.TaskRepository)
    tasks = [Mock(spec=modulo_task_service.Task)]
    repository.list_by_user.return_value = tasks
    service = modulo_task_service.TaskService(repository)

    result = service.list_tasks(7, completed, search)

    assert result is tasks
    repository.list_by_user.assert_called_once_with(7, completed, expected_search)


@pytest.mark.parametrize(
    ("counts", "expected_percentage"),
    [((4, 1, 3), 75.0), ((3, 2, 1), 33.33), ((0, 0, 0), 0.0)],
)
def test_estatisticas(modulo_task_service, counts, expected_percentage):
    repository = Mock(spec=modulo_task_service.TaskRepository)
    repository.count_by_user.return_value = counts
    service = modulo_task_service.TaskService(repository)

    result = service.get_stats(7)

    assert result.total == counts[0]
    assert result.pending == counts[1]
    assert result.completed == counts[2]
    assert result.completion_percentage == expected_percentage
    repository.count_by_user.assert_called_once_with(7)


def test_obter_tarefa_encontrada(modulo_task_service):
    repository = Mock(spec=modulo_task_service.TaskRepository)
    task = Mock(spec=modulo_task_service.Task)
    repository.get_by_id_and_user.return_value = task
    service = modulo_task_service.TaskService(repository)

    assert service.get_task(7, 11) is task
    repository.get_by_id_and_user.assert_called_once_with(11, 7)


def test_obter_tarefa_inexistente(modulo_task_service):
    repository = Mock(spec=modulo_task_service.TaskRepository)
    repository.get_by_id_and_user.return_value = None
    service = modulo_task_service.TaskService(repository)

    with pytest.raises(TaskNotFoundError) as error:
        service.get_task(7, 11)

    assert str(error.value) == ""
    repository.get_by_id_and_user.assert_called_once_with(11, 7)
    repository.save.assert_not_called()


def test_atualizar_tarefa(modulo_task_service):
    repository = Mock(spec=modulo_task_service.TaskRepository)
    task = Mock(spec=modulo_task_service.Task)
    repository.get_by_id_and_user.return_value = task
    repository.save.return_value = task
    service = modulo_task_service.TaskService(repository)
    data = TaskUpdate(title="Novo título", description=None)

    result = service.update_task(7, 11, data)

    assert result is task
    assert task.title == "Novo título"
    assert task.description is None
    repository.get_by_id_and_user.assert_called_once_with(11, 7)
    repository.save.assert_called_once_with(task)


def test_atualizar_tarefa_inexistente_nao_salva(modulo_task_service):
    repository = Mock(spec=modulo_task_service.TaskRepository)
    repository.get_by_id_and_user.return_value = None
    service = modulo_task_service.TaskService(repository)

    with pytest.raises(TaskNotFoundError):
        service.update_task(7, 11, TaskUpdate(title="Novo título"))

    repository.save.assert_not_called()


def test_concluir_tarefa_pendente(modulo_task_service):
    repository = Mock(spec=modulo_task_service.TaskRepository)
    task = Mock(spec=modulo_task_service.Task)
    task.completed = False
    repository.get_by_id_and_user.return_value = task
    repository.save.return_value = task
    service = modulo_task_service.TaskService(repository)

    result = service.complete_task(7, 11)

    assert result is task
    assert task.completed is True
    repository.get_by_id_and_user.assert_called_once_with(11, 7)
    repository.save.assert_called_once_with(task)


def test_concluir_tarefa_ja_concluida_nao_salva(modulo_task_service):
    repository = Mock(spec=modulo_task_service.TaskRepository)
    task = Mock(spec=modulo_task_service.Task)
    task.completed = True
    repository.get_by_id_and_user.return_value = task
    service = modulo_task_service.TaskService(repository)

    with pytest.raises(TaskAlreadyCompletedError) as error:
        service.complete_task(7, 11)

    assert str(error.value) == ""
    repository.save.assert_not_called()


def test_concluir_tarefa_inexistente_nao_salva(modulo_task_service):
    repository = Mock(spec=modulo_task_service.TaskRepository)
    repository.get_by_id_and_user.return_value = None
    service = modulo_task_service.TaskService(repository)

    with pytest.raises(TaskNotFoundError):
        service.complete_task(7, 11)

    repository.save.assert_not_called()


def test_excluir_tarefa(modulo_task_service):
    repository = Mock(spec=modulo_task_service.TaskRepository)
    task = Mock(spec=modulo_task_service.Task)
    repository.get_by_id_and_user.return_value = task
    service = modulo_task_service.TaskService(repository)

    assert service.delete_task(7, 11) is None
    repository.get_by_id_and_user.assert_called_once_with(11, 7)
    repository.delete.assert_called_once_with(task)


def test_excluir_tarefa_inexistente_nao_deleta(modulo_task_service):
    repository = Mock(spec=modulo_task_service.TaskRepository)
    repository.get_by_id_and_user.return_value = None
    service = modulo_task_service.TaskService(repository)

    with pytest.raises(TaskNotFoundError):
        service.delete_task(7, 11)

    repository.delete.assert_not_called()
