from types import SimpleNamespace
from unittest.mock import Mock

import pytest

from app.exceptions import TaskAlreadyCompletedError, TaskNotFoundError
from app.schemas.task_schema import TaskCreate, TaskUpdate
from app.services.task_service import TaskService


@pytest.fixture
def repository():
    return Mock()


@pytest.fixture
def service(repository):
    return TaskService(repository)


def test_create_task_encaminha_titulo_e_descricao(service, repository):
    data = TaskCreate(title="Estudar Python", description="Capítulo 1")
    expected = SimpleNamespace(title=data.title)
    repository.create.return_value = expected

    result = service.create_task(7, data)

    repository.create.assert_called_once_with(7, "Estudar Python", "Capítulo 1")
    assert result is expected


def test_list_tasks_normaliza_busca(service, repository):
    repository.list_by_user.return_value = []

    result = service.list_tasks(7, completed=False, search="  prova  ")

    repository.list_by_user.assert_called_once_with(7, False, "prova")
    assert result == []


def test_list_tasks_converte_busca_vazia_em_none(service, repository):
    service.list_tasks(7, search="   ")

    repository.list_by_user.assert_called_once_with(7, None, None)


@pytest.mark.parametrize(
    ("counts", "expected"),
    [
        ((0, 0, 0), (0, 0, 0, 0.0)),
        ((4, 1, 3), (4, 1, 3, 75.0)),
    ],
)
def test_get_stats_calcula_percentual(service, repository, counts, expected):
    repository.count_by_user.return_value = counts

    result = service.get_stats(7)

    repository.count_by_user.assert_called_once_with(7)
    assert (result.total, result.pending, result.completed, result.completion_percentage) == expected


def test_get_task_retorna_tarefa_do_usuario(service, repository):
    task = SimpleNamespace(id=12)
    repository.get_by_id_and_user.return_value = task

    assert service.get_task(7, 12) is task
    repository.get_by_id_and_user.assert_called_once_with(12, 7)


def test_get_task_inexistente_lanca_erro(service, repository):
    repository.get_by_id_and_user.return_value = None

    with pytest.raises(TaskNotFoundError):
        service.get_task(7, 12)


def test_update_task_altera_e_salva_tarefa(service, repository):
    task = SimpleNamespace(title="Antigo", description=None)
    repository.get_by_id_and_user.return_value = task
    repository.save.return_value = task
    data = TaskUpdate(title="Novo título", description="Detalhes")

    result = service.update_task(7, 12, data)

    assert (task.title, task.description) == ("Novo título", "Detalhes")
    repository.save.assert_called_once_with(task)
    assert result is task


def test_complete_task_marca_e_salva_tarefa(service, repository):
    task = SimpleNamespace(completed=False)
    repository.get_by_id_and_user.return_value = task
    repository.save.return_value = task

    result = service.complete_task(7, 12)

    assert task.completed is True
    repository.save.assert_called_once_with(task)
    assert result is task


def test_complete_task_ja_concluida_lanca_erro(service, repository):
    repository.get_by_id_and_user.return_value = SimpleNamespace(completed=True)

    with pytest.raises(TaskAlreadyCompletedError):
        service.complete_task(7, 12)

    repository.save.assert_not_called()


def test_delete_task_busca_e_remove(service, repository):
    task = SimpleNamespace(id=12)
    repository.get_by_id_and_user.return_value = task

    assert service.delete_task(7, 12) is None
    repository.delete.assert_called_once_with(task)
