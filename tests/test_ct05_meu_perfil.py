"""CT-05 | Meu perfil | Acessar o perfil."""


def test_ct05_perfil_retorna_dados_do_usuario_autenticado(client, usuario_cadastrado, headers_autenticados):
    """CT-05: a API deve retornar os dados do perfil autenticado."""
    resposta = client.get("/users/me", headers=headers_autenticados)

    assert resposta.status_code == 200
    assert resposta.json()["id"] == usuario_cadastrado["id"]
    assert resposta.json()["name"] == usuario_cadastrado["name"]
    assert resposta.json()["email"] == usuario_cadastrado["email"]
    sem_token = client.get("/users/me")
    assert sem_token.status_code == 401
    assert sem_token.json()["detail"]
