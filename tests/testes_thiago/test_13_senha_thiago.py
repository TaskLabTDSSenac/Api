def test_ct13_alteracao_de_senha_com_senha_atual_incorreta(client):
    """CT-13: a API deve rejeitar a senha atual incorreta."""
    usuario = {
        "name": "Thiago Teste",
        "email": "ct13@example.com",
        "password": "12345678",
    }
    client.post("/auth/register", json=usuario)
    login = client.post(
        "/auth/login",
        json={"email": usuario["email"], "password": usuario["password"]},
    )
    cabecalhos = {"Authorization": f"Bearer {login.json()['access_token']}"}

    resposta = client.patch(
        "/users/me/password",
        json={
            "current_password": "senha-incorreta",
            "new_password": "NovaSenha123",
        },
        headers=cabecalhos,
    )

    assert resposta.status_code == 400
    assert resposta.json()["detail"] == "Senha atual incorreta."
