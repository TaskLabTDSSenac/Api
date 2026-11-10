def test_logincarlosd_autentica_email_normalizado_no_cadastro(client):
    """O login deve aceitar o e-mail normalizado durante o cadastro."""
    dados = {
        "name": "Carlos Daniel Login",
        "email": "  Carlos.Daniel.Login.Normalizado@example.com  ",
        "password": "SenhaValida123",
    }
    cadastro = client.post("/auth/register", json=dados)
    assert cadastro.status_code == 201

    resposta = client.post(
        "/auth/login",
        json={
            "email": "carlos.daniel.login.normalizado@example.com",
            "password": dados["password"],
        },
    )

    assert resposta.status_code == 200
    assert resposta.json()["access_token"]
    assert resposta.json()["token_type"] == "bearer"
