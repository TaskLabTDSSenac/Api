def test_ct08_concluir_tarefa_altera_status(client):
    """CT-08: concluir uma tarefa deve marcá-la como concluída."""
    client.post("/auth/register", json={
        "name": "CT08",
        "email": "ct08@example.com",
        "password": "SenhaValida123",
    })
    token = client.post("/auth/login", json={
        "email": "ct08@example.com",
        "password": "SenhaValida123",
    }).json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    tarefa = client.post("/tasks", headers=headers, json={
        "title": "Concluir tarefa",
    }).json()

    resposta = client.patch(f"/tasks/{tarefa['id']}/complete", headers=headers)

    assert resposta.status_code == 200
    assert resposta.json()["completed"] is True
