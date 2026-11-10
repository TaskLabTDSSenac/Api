def test_ct03_login_com_sucesso_retorna_token_bearer(client):
    """CT-03: credenciais válidas devem retornar um token de autenticação."""
    dados = {
        "name": "Carlos Daniel CT03",
        "email": "carlosdaniel.ct03@example.com",
        "password": "SenhaValida123",
    }
    cadastro = client.post("/auth/register", json=dados)
    assert cadastro.status_code == 201

    resposta = client.post(
        "/auth/login",
        json={"email": dados["email"], "password": dados["password"]},
    )

    assert resposta.status_code == 200
    corpo = resposta.json()
    assert set(corpo) == {"access_token", "token_type"}
    assert isinstance(corpo["access_token"], str)
    assert corpo["access_token"]
    assert corpo["token_type"] == "bearer"
