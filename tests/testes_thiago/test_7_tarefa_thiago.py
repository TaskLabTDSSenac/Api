def test_ct07_criacao_de_tarefa_sem_titulo(client):
    """CT-07: a API deve rejeitar a criação de tarefa sem título."""
    usuario = {
        "name": "Thiago Teste",
        "email": "ct07@example.com",
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
        json={"description": "Tarefa sem título"},
        headers=cabecalhos,
    )

    assert resposta.status_code == 422
