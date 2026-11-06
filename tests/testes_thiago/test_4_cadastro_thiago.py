def test_ct04_cadastro_rejeita_email_ja_cadastrado(client):
    """CT-04: a API deve rejeitar um e-mail que já foi cadastrado."""
    dados = {
        "name": "Thiago Teste",
        "email": "ct04@example.com",
        "password": "12345678",
    }
    cadastro = client.post("/auth/register", json=dados)
    assert cadastro.status_code == 201

    resposta = client.post("/auth/register", json=dados)

    assert resposta.status_code == 409
    assert resposta.json()["detail"] == "E-mail já cadastrado."
