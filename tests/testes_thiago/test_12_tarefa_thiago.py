def test_ct12_exclusao_de_tarefa_existente(client):
    """CT-12: a API deve excluir uma tarefa existente."""
    usuario = {
        "name": "Thiago Teste",
        "email": "ct12@example.com",
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
        json={"title": "Tarefa para excluir"},
        headers=cabecalhos,
    )
    tarefa_id = tarefa.json()["id"]

    resposta = client.delete(f"/tasks/{tarefa_id}", headers=cabecalhos)

    assert resposta.status_code == 204
    assert client.get(f"/tasks/{tarefa_id}", headers=cabecalhos).status_code == 404
