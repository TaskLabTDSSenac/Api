def test_registro_de_nova_missao(client, novo_usuario):
    email, senha = novo_usuario
    login = client.post("/auth/login", json={"email": email, "password": senha})
    assert login.status_code == 200
    token = login.json()["access_token"]

    resposta = client.post(
        "/tasks",
        headers={"Authorization": f"Bearer {token}"},
        json={"title": "Concluir atividade", "description": "Registrar uma nova missão"},
    )

    assert resposta.status_code == 201
    assert resposta.json()["title"] == "Concluir atividade"
