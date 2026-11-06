def test_ct06_criacao_de_tarefa_com_todos_os_campos(client):
    """CT-06: a API deve permitir criar uma tarefa com título e descrição."""
    usuario = {
        "name": "Thiago Teste",
        "email": "ct06@example.com",
        "password": "12345678",
    }
    client.post("/auth/register", json=usuario)
    login = client.post(
        "/auth/login",
        json={"email": usuario["email"], "password": usuario["password"]},
    )
    cabecalhos = {"Authorization": f"Bearer {login.json()['access_token']}"}
    dados = {"title": "Tarefa CT-06", "description": "Descrição da tarefa"}

    resposta = client.post("/tasks", json=dados, headers=cabecalhos)

    assert resposta.status_code == 201
    assert resposta.json()["title"] == dados["title"]
    assert resposta.json()["description"] == dados["description"]
