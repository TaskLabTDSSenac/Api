def test_ct04_criar_tarefa_aceita_descricao_com_acentos(client):
    """CT-04: criar tarefa com descrição contendo acentos."""
    cadastro = client.post("/auth/register", json={
        "name": "CT04",
        "email": "ct04@example.com",
        "password": "SenhaValida123",
    })
    token = client.post("/auth/login", json={
        "email": "ct04@example.com",
        "password": "SenhaValida123",
    }).json()["access_token"]

    resposta = client.post("/tasks", headers={
        "Authorization": f"Bearer {token}",
    }, json={
        "title": "Revisar matéria",
        "description": "Estudar português, ação e organização.",
    })

    assert cadastro.status_code == 201
    assert resposta.status_code == 201
    assert resposta.json()["description"] == "Estudar português, ação e organização."
