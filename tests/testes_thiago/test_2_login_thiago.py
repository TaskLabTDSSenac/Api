def test_ct02_login_com_dados_corretos(client):
    """CT-02: a API deve autorizar o acesso ao sistema."""
    dados = {
        "email": "thiago@gmail.com",
        "password": "12345678",
    }

    resposta = client.post("/auth/login", json=dados)

    assert resposta.status_code == 200