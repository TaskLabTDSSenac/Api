def test_ct09_excluir_tarefa_remove_da_lista(client):
    """CT-09: excluir uma tarefa deve removê-la da lista do usuário."""
    client.post("/auth/register", json={
        "name": "CT09",
        "email": "ct09@example.com",
        "password": "SenhaValida123",
    })
    token = client.post("/auth/login", json={
        "email": "ct09@example.com",
        "password": "SenhaValida123",
    }).json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    tarefa = client.post("/tasks", headers=headers, json={
        "title": "Excluir tarefa",
    }).json()

    resposta_exclusao = client.delete(f"/tasks/{tarefa['id']}", headers=headers)
    resposta_lista = client.get("/tasks", headers=headers)

    assert resposta_exclusao.status_code == 204
    assert all(item["id"] != tarefa["id"] for item in resposta_lista.json())
