def test_ct11_login_rejeita_email_invalido(client):
    """CT-11: login com e-mail em formato inválido deve exibir erro de validação."""
    resposta = client.post("/auth/login", json={
        "email": "email-sem-formato-valido",
        "password": "SenhaValida123",
    })

    assert resposta.status_code == 422
