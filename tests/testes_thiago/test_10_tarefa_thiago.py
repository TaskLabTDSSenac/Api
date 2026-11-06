def test_ct10_edicao_de_tarefa_existente(client):
    """CT-10: a API deve atualizar o título de uma tarefa existente."""
    usuario = {
        "name": "Thiago Teste",
        "email": "ct10@example.com",
        "password": "12345678",
    }
    client.post("/auth/register", json=usuario)
    login = client.post(
        "/auth/login",
        json={"email": usuario["email"], "password": usuario["password"]},
    )
    cabecalhos = {"Authorization": f"Bearer {login.json()['access_token']}"}
    tarefa = client.post(
        "/tasks",
        json={"title": "Título original", "description": "Descrição da tarefa"},
        headers=cabecalhos,
    )

    resposta = client.put(
        f"/tasks/{tarefa.json()['id']}",
        json={"title": "Título atualizado", "description": "Descrição da tarefa"},
        headers=cabecalhos,
    )

    assert resposta.status_code == 200
    assert resposta.json()["title"] == "Título atualizado"
