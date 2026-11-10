def test_ct10_login_com_email_nao_cadastrado_retorna_401(client):
    """CT-10: e-mail válido mas não cadastrado deve receber HTTP 401."""
    cadastro = client.post(
        "/auth/register",
        json={
            "name": "Carlos Daniel CT10",
            "email": "carlosdaniel.ct10-cadastrado@example.com",
            "password": "SenhaValida123",
        },
    )
    assert cadastro.status_code == 201

    resposta = client.post(
        "/auth/login",
        json={
            "email": "carlosdaniel.nao-cadastrado@example.com",
            "password": "SenhaValida123",
        },
    )

    assert resposta.status_code == 401
    assert resposta.json() == {"detail": "E-mail ou senha inválidos."}
