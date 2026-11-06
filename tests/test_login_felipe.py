def test_ct01_login_com_senha_incorreta(client):
    """CT-01: O sistema deve rejeitar o login e exibir mensagem de erro."""
    dados = {
        "email": "ct01@example.com",
        "password": "senhaerrada123",
    }

    resposta = client.post("/auth/login", json=dados)

    assert resposta.status_code == 401


def test_ct02_login_com_email_incorreto(client):
    """CT-02: O sistema deve rejeitar o login e exibir mensagem de erro."""
    dados = {
        "email": "invalido@gmail.com",
        "password": "Teste11!",
    }

    resposta = client.post("/auth/login", json=dados)

    assert resposta.status_code == 401

def test_ct06_criar_tarefa_com_titulo_vazio(client, auth_headers):
    """CT-06: O sistema deve rejeitar a criação da tarefa e exibir mensagem de erro."""
    dados = {
        "title": "",
        "description": "Teste sem titulo",
    }

    resposta = client.post(
        "/tasks",
        json=dados,
        headers=auth_headers,
    )

    assert resposta.status_code == 422


def test_ct07_criar_tarefa_com_sucesso(client, auth_headers):
    """CT-07: usuário autenticado consegue criar uma tarefa."""
    resposta = client.post(
        "/tasks",
        json={"title": "Minha tarefa de teste", "description": "Criada com pytest"},
        headers=auth_headers,
    )

    assert resposta.status_code == 201
    tarefa = resposta.json()
    assert tarefa["title"] == "Minha tarefa de teste"
    assert tarefa["description"] == "Criada com pytest"
    assert tarefa["completed"] is False


def test_ct08_visualizar_tarefas_criadas(client, auth_headers):
    """CT-08: usuário autenticado consegue visualizar suas tarefas."""
    criada = client.post(
        "/tasks",
        json={"title": "Tarefa para visualizar"},
        headers=auth_headers,
    )
    assert criada.status_code == 201

    resposta = client.get("/tasks", headers=auth_headers)

    assert resposta.status_code == 200
    assert any(tarefa["id"] == criada.json()["id"] for tarefa in resposta.json())


def test_ct09_editar_tarefa_existente(client, auth_headers):
    """CT-09: usuário autenticado consegue editar uma tarefa existente."""
    criada = client.post(
        "/tasks",
        json={"title": "Título antes da edição"},
        headers=auth_headers,
    )
    assert criada.status_code == 201
    task_id = criada.json()["id"]

    resposta = client.put(
        f"/tasks/{task_id}",
        json={"title": "Título depois da edição"},
        headers=auth_headers,
    )

    assert resposta.status_code == 200
    assert resposta.json()["title"] == "Título depois da edição"


def test_ct10_excluir_tarefa_existente(client, auth_headers):
    """CT-10: usuário autenticado consegue excluir uma tarefa existente."""
    criada = client.post(
        "/tasks",
        json={"title": "Tarefa para excluir"},
        headers=auth_headers,
    )
    assert criada.status_code == 201
    task_id = criada.json()["id"]

    resposta = client.delete(f"/tasks/{task_id}", headers=auth_headers)

    assert resposta.status_code == 204
    consulta = client.get(f"/tasks/{task_id}", headers=auth_headers)
    assert consulta.status_code == 404


def test_ct11_concluir_tarefa_existente(client, auth_headers):
    """CT-11: usuário autenticado consegue concluir uma tarefa pendente."""
    criada = client.post(
        "/tasks",
        json={"title": "Tarefa para concluir"},
        headers=auth_headers,
    )
    assert criada.status_code == 201
    task_id = criada.json()["id"]

    resposta = client.patch(f"/tasks/{task_id}/complete", headers=auth_headers)

    assert resposta.status_code == 200
    assert resposta.json()["completed"] is True
