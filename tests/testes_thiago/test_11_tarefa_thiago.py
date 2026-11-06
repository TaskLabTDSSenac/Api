def test_ct11_conclusao_de_tarefa_existente(client):
    """CT-11: a API deve marcar uma tarefa existente como concluída."""
    usuario = {
        "name": "Thiago Teste",
        "email": "ct11@example.com",
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
        json={"title": "Tarefa para concluir"},
        headers=cabecalhos,
    )

    resposta = client.patch(
        f"/tasks/{tarefa.json()['id']}/complete",
        headers=cabecalhos,
    )

    assert resposta.status_code == 200
    assert resposta.json()["completed"] is True
