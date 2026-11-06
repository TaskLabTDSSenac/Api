def test_login_com_senha_incorreta(client):
    email = "kauane.ct01@example.com"
    cadastro = client.post(
        "/auth/register",
        json={"name": "Usuária CT01", "email": email, "password": "SenhaCorreta123"},
    )
    assert cadastro.status_code == 201

    resposta = client.post(
        "/auth/login", json={"email": email, "password": "SenhaErrada123"}
    )

    assert resposta.status_code == 401
