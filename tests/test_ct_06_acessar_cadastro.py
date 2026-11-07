def test_ct06_rota_de_cadastro_aceita_novo_usuario(client):
    """CT-06: a rota de cadastro deve aceitar e retornar um novo usuário."""
    resposta = client.post("/auth/register", json={
        "name": "CT06",
        "email": "ct06@example.com",
        "password": "SenhaValida123",
    })

    assert resposta.status_code == 201
    assert resposta.json()["email"] == "ct06@example.com"
