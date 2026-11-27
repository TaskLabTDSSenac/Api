from unittest.mock import Mock

import pytest

from app.exceptions import TaskAlreadyCompletedError, TaskNotFoundError
from app.schemas.task_schema import TaskCreate, TaskUpdate


@pytest.fixture
def modulo_task_service(test_settings):
    from app.services import task_service
    return task_service


def test_criar_tarefa_com_sucesso(modulo_task_service):
    repository = Mock(spec=modulo_task_service.TaskRepository)
    tarefa = Mock(spec=modulo_task_service.Task)
    repository.create.return_value = tarefa
    service = modulo_task_service.TaskService(repository)
    dados = TaskCreate(title="Estudar testes", description="Praticar pytest")
    user_id = 20

    resultado = service.create_task(user_id, dados)

    assert resultado is tarefa
    repository.create.assert_called_once_with(
        user_id, dados.title, dados.description
    )


def test_listar_tarefas_com_busca(modulo_task_service):
    repository = Mock(spec=modulo_task_service.TaskRepository)
    tarefas = [Mock(spec=modulo_task_service.Task)]
    repository.list_by_user.return_value = tarefas
    service = modulo_task_service.TaskService(repository)
    user_id = 20
    search = "  relatório  "

    resultado = service.list_tasks(user_id, completed=True, search=search)

    assert resultado is tarefas
    repository.list_by_user.assert_called_once_with(user_id, True, "relatório")


def test_listar_tarefas_sem_busca(modulo_task_service):
    repository = Mock(spec=modulo_task_service.TaskRepository)
    tarefas = []
    repository.list_by_user.return_value = tarefas
    service = modulo_task_service.TaskService(repository)
    user_id = 20

    resultado = service.list_tasks(user_id)

    assert resultado is tarefas
    repository.list_by_user.assert_called_once_with(user_id, None, None)


def test_excluir_tarefa_encontrada(modulo_task_service):
    repository = Mock(spec=modulo_task_service.TaskRepository)
    tarefa = Mock(spec=modulo_task_service.Task)
    repository.get_by_id_and_user.return_value = tarefa
    service = modulo_task_service.TaskService(repository)
    user_id = 20
    task_id = 5

    resultado = service.delete_task(user_id, task_id)

    assert resultado is None
    repository.get_by_id_and_user.assert_called_once_with(task_id, user_id)
    repository.delete.assert_called_once_with(tarefa)


def test_excluir_tarefa_inexistente(modulo_task_service):
    repository = Mock(spec=modulo_task_service.TaskRepository)
    repository.get_by_id_and_user.return_value = None
    service = modulo_task_service.TaskService(repository)
    user_id = 20
    task_id = 99

    with pytest.raises(TaskNotFoundError):
        service.delete_task(user_id, task_id)

    repository.get_by_id_and_user.assert_called_once_with(task_id, user_id)
    repository.delete.assert_not_called()


def test_atualizar_tarefa_inexistente(modulo_task_service):
    repository = Mock(spec=modulo_task_service.TaskRepository)
    repository.get_by_id_and_user.return_value = None
    service = modulo_task_service.TaskService(repository)
    user_id = 20
    task_id = 99
    dados = TaskUpdate(title="Novo título", description="Nova descrição")

    with pytest.raises(TaskNotFoundError):
        service.update_task(user_id, task_id, dados)

    repository.get_by_id_and_user.assert_called_once_with(task_id, user_id)
    repository.save.assert_not_called()


def test_atualizar_tarefa_encontrada(modulo_task_service):
    repository = Mock(spec=modulo_task_service.TaskRepository)
    tarefa = Mock(spec=modulo_task_service.Task)
    repository.get_by_id_and_user.return_value = tarefa
    repository.save.return_value = tarefa
    service = modulo_task_service.TaskService(repository)
    user_id = 20
    task_id = 5
    dados = TaskUpdate(title="Título atualizado", description="Descrição atualizada")

    resultado = service.update_task(user_id, task_id, dados)

    assert tarefa.title == dados.title
    assert tarefa.description == dados.description
    assert resultado is tarefa
    repository.get_by_id_and_user.assert_called_once_with(task_id, user_id)
    repository.save.assert_called_once_with(tarefa)


def test_concluir_tarefa_pendente(modulo_task_service):
    repository = Mock(spec=modulo_task_service.TaskRepository)
    tarefa = Mock(spec=modulo_task_service.Task)
    tarefa.completed = False
    repository.get_by_id_and_user.return_value = tarefa
    repository.save.return_value = tarefa
    service = modulo_task_service.TaskService(repository)
    user_id = 20
    task_id = 5

    resultado = service.complete_task(user_id, task_id)

    assert tarefa.completed is True
    assert resultado is tarefa
    repository.get_by_id_and_user.assert_called_once_with(task_id, user_id)
    repository.save.assert_called_once_with(tarefa)


def test_concluir_tarefa_ja_concluida(modulo_task_service):
    repository = Mock(spec=modulo_task_service.TaskRepository)
    tarefa = Mock(spec=modulo_task_service.Task)
    tarefa.completed = True
    repository.get_by_id_and_user.return_value = tarefa
    service = modulo_task_service.TaskService(repository)
    user_id = 20
    task_id = 5

    with pytest.raises(TaskAlreadyCompletedError):
        service.complete_task(user_id, task_id)

    repository.get_by_id_and_user.assert_called_once_with(task_id, user_id)
    repository.save.assert_not_called()
