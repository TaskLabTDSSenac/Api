from unittest.mock import Mock

import pytest

from app.exceptions import TaskAlreadyCompletedError, TaskNotFoundError
from app.models.task import Task
from app.schemas.task_schema import TaskCreate, TaskUpdate
from app.services.task_service import TaskService


@pytest.fixture
def repository():
    return Mock()


@pytest.fixture
def service(repository):
    return TaskService(repository)


def make_task(**overrides):
    values = {"id": 7, "user_id": 3, "title": "Original", "description": "Texto", "completed": False}
    values.update(overrides)
    return Task(**values)


def test_create_task_delegates_to_repository(service, repository):
    data = TaskCreate(title="Nova tarefa", description="Detalhes")
    expected = make_task(title=data.title, description=data.description)
    repository.create.return_value = expected

    result = service.create_task(3, data)

    assert result is expected
    repository.create.assert_called_once_with(3, "Nova tarefa", "Detalhes")


@pytest.mark.parametrize(("search", "expected"), [("  relatório  ", "relatório"), ("   ", None), (None, None)])
def test_list_tasks_normalizes_search(service, repository, search, expected):
    repository.list_by_user.return_value = []

    assert service.list_tasks(3, completed=False, search=search) == []

    repository.list_by_user.assert_called_once_with(3, False, expected)


def test_get_stats_calculates_rounded_percentage(service, repository):
    repository.count_by_user.return_value = (6, 2, 4)

    result = service.get_stats(3)

    assert (result.total, result.pending, result.completed) == (6, 2, 4)
    assert result.completion_percentage == 66.67
    repository.count_by_user.assert_called_once_with(3)


def test_get_stats_returns_zero_percentage_without_tasks(service, repository):
    repository.count_by_user.return_value = (0, 0, 0)

    assert service.get_stats(3).completion_percentage == 0.0


def test_get_task_returns_task(service, repository):
    expected = make_task()
    repository.get_by_id_and_user.return_value = expected

    assert service.get_task(3, 7) is expected
    repository.get_by_id_and_user.assert_called_once_with(7, 3)


def test_get_task_raises_when_missing(service, repository):
    repository.get_by_id_and_user.return_value = None

    with pytest.raises(TaskNotFoundError):
        service.get_task(3, 99)


def test_update_task_changes_fields_and_saves(service, repository):
    task = make_task()
    repository.get_by_id_and_user.return_value = task
    repository.save.return_value = task

    result = service.update_task(3, 7, TaskUpdate(title="Atualizada", description=None))

    assert result is task
    assert (task.title, task.description) == ("Atualizada", None)
    repository.save.assert_called_once_with(task)


def test_complete_task_marks_pending_task_completed(service, repository):
    task = make_task()
    repository.get_by_id_and_user.return_value = task
    repository.save.return_value = task

    assert service.complete_task(3, 7) is task
    assert task.completed is True
    repository.save.assert_called_once_with(task)


def test_complete_task_raises_when_already_completed(service, repository):
    task = make_task(completed=True)
    repository.get_by_id_and_user.return_value = task

    with pytest.raises(TaskAlreadyCompletedError):
        service.complete_task(3, 7)

    repository.save.assert_not_called()


def test_delete_task_delegates_to_repository(service, repository):
    task = make_task()
    repository.get_by_id_and_user.return_value = task

    assert service.delete_task(3, 7) is None
    repository.delete.assert_called_once_with(task)
