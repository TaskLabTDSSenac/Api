def test_ct05_editar_tarefa_atualiza_dados(client):
    """CT-05: edição deve devolver a tarefa com os novos dados."""
    client.post("/auth/register", json={
        "name": "CT05",
        "email": "ct05@example.com",
        "password": "SenhaValida123",
    })
    token = client.post("/auth/login", json={
        "email": "ct05@example.com",
        "password": "SenhaValida123",
    }).json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    tarefa = client.post("/tasks", headers=headers, json={
        "title": "Tarefa original",
        "description": "Descrição original",
    }).json()

    resposta = client.put(f"/tasks/{tarefa['id']}", headers=headers, json={
        "title": "Tarefa atualizada",
        "description": "Descrição atualizada",
    })

    assert resposta.status_code == 200
    assert resposta.json()["title"] == "Tarefa atualizada"
    assert resposta.json()["description"] == "Descrição atualizada"
