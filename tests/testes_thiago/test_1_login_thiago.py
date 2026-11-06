def test_ct00_cadastro_com_dados_corretos(client):
    """CT-00: a API deve autorizar o cadastro."""
    dados = {
        "name": "Thiago",
        "email": "thiago@gmail.com",
        "password": "12345678",
    }

    resposta = client.post("/auth/register", json=dados)

    assert resposta.status_code == 201




def test_ct01_login_com_senha_incorreta(client):
    """CT-01: a API deve rejeitar um login com a senha incorreta."""
    dados = {
        "email": "thiago@gmail.com",
        "password": "55555555",
    }

    resposta = client.post("/auth/login", json=dados)

    assert resposta.status_code == 401
