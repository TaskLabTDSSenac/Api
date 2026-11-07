def test_ct01_login_rejeita_senha_incorreta(client):
    """CT-01: login com e-mail cadastrado e senha errada deve falhar."""
    client.post("/auth/register", json={
        "name": "CT01",
        "email": "ct01@example.com",
        "password": "SenhaCorreta123",
    })

    resposta = client.post("/auth/login", json={
        "email": "ct01@example.com",
        "password": "SenhaErrada123",
    })

    assert resposta.status_code == 401
    assert "inválidos" in resposta.json()["detail"]
