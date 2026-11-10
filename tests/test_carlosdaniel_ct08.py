def test_ct08_login_com_senha_em_branco_retorna_erro_de_validacao(client):
    """CT-08: senha vazia deve ser rejeitada com HTTP 422."""
    resposta = client.post(
        "/auth/login",
        json={"email": "carlosdaniel.ct08@example.com", "password": ""},
    )

    assert resposta.status_code == 422
    erros = resposta.json()["detail"]
    erro_senha = next(erro for erro in erros if erro["loc"][-1] == "password")
    assert erro_senha["loc"] == ["body", "password"]
    assert isinstance(erro_senha["msg"], str)
    assert isinstance(erro_senha["type"], str)
