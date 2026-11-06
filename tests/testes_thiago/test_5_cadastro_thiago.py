def test_ct05_cadastro_com_dados_corretos(client):
    """CT-05: a API deve autorizar o cadastro de um novo usuário."""
    dados = {
        "name": "Thiago Teste",
        "email": "ct05@example.com",
        "password": "12345678",
    }

    resposta = client.post("/auth/register", json=dados)

    assert resposta.status_code == 201
    assert resposta.json()["email"] == dados["email"]
