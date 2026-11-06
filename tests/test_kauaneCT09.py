def test_usuario_edita_dados_do_perfil(client, usuario_autenticado):
    resposta = client.patch(
        "/users/me",
        headers=usuario_autenticado["headers"],
        json={"name": "Nome atualizado"},
    )

    assert resposta.status_code == 200
    assert resposta.json()["name"] == "Nome atualizado"
