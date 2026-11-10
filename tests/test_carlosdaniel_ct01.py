def test_ct01_login_rejeita_senha_incorreta(client):
    """CT-01: credenciais com senha incorreta devem receber HTTP 401."""
    dados = {
        "name": "Carlos Daniel CT01",
        "email": "carlosdaniel.ct01@example.com",
        "password": "SenhaValida123",
    }
    cadastro = client.post("/auth/register", json=dados)
    assert cadastro.status_code == 201

    resposta = client.post(
        "/auth/login",
        json={"email": dados["email"], "password": "SenhaIncorreta123"},
    )

    assert resposta.status_code == 401
    assert resposta.json() == {"detail": "E-mail ou senha inválidos."}
    assert resposta.headers["www-authenticate"] == "Bearer"
