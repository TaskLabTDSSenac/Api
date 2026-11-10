def test_ct09_cadastro_rejeita_senha_fraca(client):
    """CT-09: senha abaixo do mínimo aceito deve retornar HTTP 422."""
    resposta = client.post(
        "/auth/register",
        json={
            "name": "Carlos Daniel CT09",
            "email": "carlosdaniel.ct09@example.com",
            "password": "12345",
        },
    )

    assert resposta.status_code == 422
    erros = resposta.json()["detail"]
    erro_senha = next(erro for erro in erros if erro["loc"][-1] == "password")
    assert erro_senha["loc"] == ["body", "password"]
    assert isinstance(erro_senha["msg"], str)
    assert isinstance(erro_senha["type"], str)
    assert "input" not in erro_senha
