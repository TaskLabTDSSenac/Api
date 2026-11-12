"""CT-09 | Excluir tarefa | Excluir tarefa criada."""


import pytest


@pytest.mark.xfail(reason="A API responde 204, mas TaskService.delete_task não chama TaskRepository.delete e o registro permanece.")
def test_ct09_excluir_tarefa_remove_da_listagem(client, headers_autenticados):
    """CT-09: a API deve excluir a tarefa e removÃª-la da listagem."""
    criada = client.post("/tasks", json={"title": "Tarefa CT-09", "description": "Excluir"}, headers=headers_autenticados)
    task_id = criada.json()["id"]

    resposta = client.delete(f"/tasks/{task_id}", headers=headers_autenticados)
    listagem = client.get("/tasks", headers=headers_autenticados)

    assert criada.status_code == 201
    assert resposta.status_code == 204
    assert resposta.content == b""
    assert all(tarefa["id"] != task_id for tarefa in listagem.json())

