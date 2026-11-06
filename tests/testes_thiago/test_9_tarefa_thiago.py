def test_ct09_visualizacao_de_tarefa_existente(client):
    """CT-09: a API deve exibir os detalhes de uma tarefa existente."""
    usuario = {
        "name": "Thiago Teste",
        "email": "ct09@example.com",
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
        json={"title": "Tarefa CT-09", "description": "Tarefa para visualizar"},
        headers=cabecalhos,
    )

    resposta = client.get(f"/tasks/{tarefa.json()['id']}", headers=cabecalhos)

    assert resposta.status_code == 200
    assert resposta.json()["title"] == "Tarefa CT-09"
    assert resposta.json()["description"] == "Tarefa para visualizar"
