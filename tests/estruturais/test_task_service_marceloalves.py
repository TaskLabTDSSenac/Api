from unittest.mock import Mock

import pytest


@pytest.fixture
def task_service_module(test_settings):
    from app.services import task_service

    return task_service


def test_create_task_delegates_to_repository(task_service_module):
    repository = Mock(spec=task_service_module.TaskRepository)
    task = Mock(spec=task_service_module.Task)
    repository.create.return_value = task
    service = task_service_module.TaskService(repository)
    data = task_service_module.TaskCreate(title="  Revisar API  ", description=" testes ")

    result = service.create_task(12, data)

    assert result is task
    repository.create.assert_called_once_with(12, data.title, data.description)


def test_list_tasks_strips_search_and_passes_filters(task_service_module):
    repository = Mock(spec=task_service_module.TaskRepository)
    tasks = [Mock(spec=task_service_module.Task)]
    repository.list_by_user.return_value = tasks
    service = task_service_module.TaskService(repository)

    result = service.list_tasks(4, completed=False, search="  Relatório  ")

    assert result is tasks
    repository.list_by_user.assert_called_once_with(4, False, "Relatório")


def test_list_tasks_turns_blank_search_into_none(task_service_module):
    repository = Mock(spec=task_service_module.TaskRepository)
    service = task_service_module.TaskService(repository)

    service.list_tasks(4, search="   ")

    repository.list_by_user.assert_called_once_with(4, None, None)


def test_get_stats_calculates_percentage(task_service_module):
    repository = Mock(spec=task_service_module.TaskRepository)
    repository.count_by_user.return_value = (3, 2, 1)
    service = task_service_module.TaskService(repository)

    result = service.get_stats(9)

    assert result.total == 3
    assert result.pending == 2
    assert result.completed == 1
    assert result.completion_percentage == 33.33
    repository.count_by_user.assert_called_once_with(9)


def test_get_stats_with_no_tasks_returns_zero_percentage(task_service_module):
    repository = Mock(spec=task_service_module.TaskRepository)
    repository.count_by_user.return_value = (0, 0, 0)
    service = task_service_module.TaskService(repository)

    result = service.get_stats(9)

    assert result.completion_percentage == 0.0


def test_get_task_returns_task_found_for_user(task_service_module):
    repository = Mock(spec=task_service_module.TaskRepository)
    task = Mock(spec=task_service_module.Task)
    repository.get_by_id_and_user.return_value = task
    service = task_service_module.TaskService(repository)

    assert service.get_task(5, 21) is task
    repository.get_by_id_and_user.assert_called_once_with(21, 5)


def test_get_task_raises_when_task_is_missing_or_not_owned(task_service_module):
    repository = Mock(spec=task_service_module.TaskRepository)
    repository.get_by_id_and_user.return_value = None
    service = task_service_module.TaskService(repository)

    with pytest.raises(task_service_module.TaskNotFoundError):
        service.get_task(5, 21)


def test_update_task_changes_fields_and_saves(task_service_module):
    repository = Mock(spec=task_service_module.TaskRepository)
    task = Mock(spec=task_service_module.Task)
    repository.get_by_id_and_user.return_value = task
    repository.save.return_value = task
    service = task_service_module.TaskService(repository)
    data = task_service_module.TaskUpdate(title="Título novo", description="Descrição nova")

    result = service.update_task(5, 21, data)

    assert task.title == "Título novo"
    assert task.description == "Descrição nova"
    assert result is task
    repository.save.assert_called_once_with(task)


def test_complete_task_marks_pending_task_completed_and_saves(task_service_module):
    repository = Mock(spec=task_service_module.TaskRepository)
    task = Mock(spec=task_service_module.Task)
    task.completed = False
    repository.get_by_id_and_user.return_value = task
    repository.save.return_value = task
    service = task_service_module.TaskService(repository)

    result = service.complete_task(5, 21)

    assert task.completed is True
    assert result is task
    repository.save.assert_called_once_with(task)


def test_complete_task_raises_if_already_completed(task_service_module):
    repository = Mock(spec=task_service_module.TaskRepository)
    task = Mock(spec=task_service_module.Task)
    task.completed = True
    repository.get_by_id_and_user.return_value = task
    service = task_service_module.TaskService(repository)

    with pytest.raises(task_service_module.TaskAlreadyCompletedError):
        service.complete_task(5, 21)

    repository.save.assert_not_called()


def test_delete_task_deletes_found_task(task_service_module):
    repository = Mock(spec=task_service_module.TaskRepository)
    task = Mock(spec=task_service_module.Task)
    repository.get_by_id_and_user.return_value = task
    service = task_service_module.TaskService(repository)

    assert service.delete_task(5, 21) is None
    repository.delete.assert_called_once_with(task)
