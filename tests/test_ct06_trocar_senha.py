"""CT-06 | Trocar senha | Trocar senha."""


def test_ct06_troca_senha_permite_nova_e_rejeita_antiga(client, usuario_cadastrado, headers_autenticados):
    """CT-06: a API deve alterar a senha e autenticar apenas com a nova senha."""
    dados = {"current_password": usuario_cadastrado["password"], "new_password": "SenhaNova456!"}

    resposta = client.patch("/users/me/password", json=dados, headers=headers_autenticados)

    assert resposta.status_code == 200
    assert resposta.json()["detail"]
    login_novo = client.post("/auth/login", json={"email": usuario_cadastrado["email"], "password": "SenhaNova456!"})
    login_antigo = client.post("/auth/login", json={"email": usuario_cadastrado["email"], "password": usuario_cadastrado["password"]})
    assert login_novo.status_code == 200
    assert login_novo.json()["access_token"]
    assert login_antigo.status_code == 401
    assert login_antigo.json()["detail"]
