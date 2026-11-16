from uuid import uuid4


def _criar_usuario_autenticado(client):
    email = f"teste.get.{uuid4().hex}@example.com"
    senha = "SenhaSegura123"
    cadastro = client.post(
        "/auth/register",
        json={"name": "Aluno GET", "email": email, "password": senha},
    )
    assert cadastro.status_code == 201

    login = client.post("/auth/login", json={"email": email, "password": senha})
    assert login.status_code == 200
    return {"Authorization": f"Bearer {login.json()['access_token']}"}


def test_ct04_get_lista_tarefas_do_usuario_autenticado(client):
    """A listagem deve retornar as tarefas do usuário autenticado."""
    headers = _criar_usuario_autenticado(client)
    criacao = client.post(
        "/tasks",
        json={"title": "Estudar GET", "description": "Testar listagem"},
        headers=headers,
    )
    assert criacao.status_code == 201

    resposta = client.get("/tasks", headers=headers)

    assert resposta.status_code == 200
    assert any(tarefa["id"] == criacao.json()["id"] for tarefa in resposta.json())


def test_ct05_get_tarefa_por_id(client):
    """A consulta por ID deve retornar os dados da tarefa existente."""
    headers = _criar_usuario_autenticado(client)
    criacao = client.post(
        "/tasks",
        json={"title": "Tarefa para consulta", "description": "Consultar por ID"},
        headers=headers,
    )
    assert criacao.status_code == 201

    resposta = client.get(f"/tasks/{criacao.json()['id']}", headers=headers)

    assert resposta.status_code == 200
    assert resposta.json()["id"] == criacao.json()["id"]
    assert resposta.json()["title"] == "Tarefa para consulta"


def test_ct06_get_estatisticas_das_tarefas(client):
    """As estatísticas devem refletir as tarefas do usuário autenticado."""
    headers = _criar_usuario_autenticado(client)
    criacao = client.post(
        "/tasks",
        json={"title": "Tarefa pendente", "description": "Contagem de tarefas"},
        headers=headers,
    )
    assert criacao.status_code == 201

    resposta = client.get("/tasks/stats", headers=headers)

    assert resposta.status_code == 200
    assert resposta.json()["total"] == 1
    assert resposta.json()["pending"] == 1
