"""CT-07 | Minhas tarefas | Listar tarefas."""


def test_ct07_listagem_retorna_tarefas_do_usuario_autenticado(client, headers_autenticados):
    """CT-07: a API deve listar as tarefas do usuário autenticado."""
    criada = client.post("/tasks", json={"title": "Tarefa CT-07", "description": "Descrição CT-07"}, headers=headers_autenticados)

    resposta = client.get("/tasks", headers=headers_autenticados)

    assert criada.status_code == 201
    assert resposta.status_code == 200
    assert any(tarefa["id"] == criada.json()["id"] for tarefa in resposta.json())
    sem_token = client.get("/tasks")
    assert sem_token.status_code == 401
    assert sem_token.json()["detail"]
