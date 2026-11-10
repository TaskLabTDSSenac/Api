def test_ct07_api_rejeita_campo_de_confirmacao_nao_suportado(client):
    """CT-07: a API deve impedir o cadastro quando recebe confirmação extra."""
    dados = {
        "name": "Carlos Daniel CT07",
        "email": "carlosdaniel.ct07@example.com",
        "password": "SenhaValida123",
        "password_confirmation": "SenhaDiferente123",
    }

    resposta = client.post("/auth/register", json=dados)

    assert resposta.status_code == 422
    erros = resposta.json()["detail"]
    erro_confirmacao = next(
        erro for erro in erros if erro["loc"][-1] == "password_confirmation"
    )
    assert erro_confirmacao["loc"] == ["body", "password_confirmation"]
    assert erro_confirmacao["type"] == "extra_forbidden"

    login = client.post(
        "/auth/login",
        json={"email": dados["email"], "password": dados["password"]},
    )
    assert login.status_code == 401
