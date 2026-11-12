"""CT-02 | Login | Entrar com a senha correta."""


def test_ct02_login_aceita_senha_correta(client, usuario_cadastrado):
    """CT-02: a API deve aceitar credenciais corretas e retornar um token Bearer."""
    dados = {"email": usuario_cadastrado["email"], "password": usuario_cadastrado["password"]}

    resposta = client.post("/auth/login", json=dados)

    assert resposta.status_code == 200
    assert resposta.json()["access_token"]
    assert resposta.json()["token_type"] == "bearer"
