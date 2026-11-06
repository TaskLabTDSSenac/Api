def test_login_com_credenciais_cadastradas(client, novo_usuario):
    email, senha = novo_usuario
    resposta = client.post("/auth/login", json={"email": email, "password": senha})

    assert resposta.status_code == 200
    assert resposta.json()["access_token"]
    assert resposta.json()["token_type"] == "bearer"
