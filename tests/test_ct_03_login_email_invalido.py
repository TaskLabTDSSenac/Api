def test_ct03_login_rejeita_email_invalido(client):
    """CT-03: login com formato de e-mail inválido deve falhar na validação."""
    resposta = client.post("/auth/login", json={
        "email": "email-invalido",
        "password": "SenhaValida123",
    })

    assert resposta.status_code == 422
