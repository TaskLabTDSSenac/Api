def test_ct08_criacao_de_tarefa_sem_descricao(client):
    """CT-08: a API deve permitir criar tarefa sem descrição."""
    usuario = {
        "name": "Thiago Teste",
        "email": "ct08@example.com",
        "password": "12345678",
    }
    client.post("/auth/register", json=usuario)
    login = client.post(
        "/auth/login",
        json={"email": usuario["email"], "password": usuario["password"]},
    )
    cabecalhos = {"Authorization": f"Bearer {login.json()['access_token']}"}

    resposta = client.post(
        "/tasks",
        json={"title": "Tarefa CT-08"},
        headers=cabecalhos,
    )

    assert resposta.status_code == 201
    assert resposta.json()["title"] == "Tarefa CT-08"
    assert resposta.json()["description"] is None
