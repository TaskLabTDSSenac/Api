from unittest.mock import Mock
import pytest
from app.schemas.task_schema import TaskCreate


@pytest.fixture
def modulo_task_service(test_settings):
    from app.services import task_service
    return task_service


def test_criar_tarefa(modulo_task_service):
    repository = Mock(spec=modulo_task_service.TaskRepository)
    tarefa = Mock(spec=modulo_task_service.Task)
    repository.create.return_value = tarefa
    service = modulo_task_service.TaskService(repository)
    dados = TaskCreate(title="Estudar testes", description="Revisar services")

    resultado = service.create_task(7, dados)

    assert resultado is tarefa
    repository.create.assert_called_once_with(7, dados.title, dados.description)

def test_listar_tarefas_com_busca_em_branco_envia_none(modulo_task_service):
    repository = Mock(spec=modulo_task_service.TaskRepository)
    service = modulo_task_service.TaskService(repository)

    service.list_tasks(7, search="   ")

    repository.list_by_user.assert_called_once_with(7, None, None)

def test_obter_estatisticas_sem_tarefas(modulo_task_service):
    repository = Mock(spec=modulo_task_service.TaskRepository)
    repository.count_by_user.return_value = (0, 0, 0)
    service = modulo_task_service.TaskService(repository)

    resultado = service.get_stats(7)

    assert resultado.completion_percentage == 0.0
    repository.count_by_user.assert_called_once_with(7)
