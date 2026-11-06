def test_usuario_sem_token_nao_acessa_perfil_apos_sair(client, novo_usuario):
    email, senha = novo_usuario
    login = client.post("/auth/login", json={"email": email, "password": senha})
    assert login.status_code == 200

    resposta = client.get("/users/me")

    assert resposta.status_code == 401
