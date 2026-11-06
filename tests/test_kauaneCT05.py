def test_login_com_nova_senha(client, novo_usuario):
    email, senha = novo_usuario
    login = client.post("/auth/login", json={"email": email, "password": senha})
    assert login.status_code == 200
    token = login.json()["access_token"]

    alteracao = client.patch(
        "/users/me/password",
        headers={"Authorization": f"Bearer {token}"},
        json={"current_password": senha, "new_password": "SenhaNova123"},
    )
    assert alteracao.status_code == 200

    resposta = client.post(
        "/auth/login", json={"email": email, "password": "SenhaNova123"}
    )

    assert resposta.status_code == 200
    assert resposta.json()["access_token"]
