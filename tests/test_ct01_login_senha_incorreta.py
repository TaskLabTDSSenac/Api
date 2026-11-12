"""CT-01 | Login | Entrar com senha incorreta."""


def test_ct01_login_rejeita_senha_incorreta(client, usuario_cadastrado):
    """CT-01: a API deve rejeitar o login com senha incorreta e informar o erro."""
    dados = {"email": usuario_cadastrado["email"], "password": "SenhaErrada123!"}

    resposta = client.post("/auth/login", json=dados)

    assert resposta.status_code == 401
    assert resposta.json()["detail"]
