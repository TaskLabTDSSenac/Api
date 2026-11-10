def test_ct11_login_com_campos_vazios_retorna_erros_de_validacao(client):
    """CT-11: ausência de e-mail e senha deve retornar HTTP 422."""
    resposta = client.post("/auth/login", json={})

    assert resposta.status_code == 422
    erros = resposta.json()["detail"]
    campos_com_erro = {erro["loc"][-1] for erro in erros}
    assert {"email", "password"}.issubset(campos_com_erro)
    assert all(erro["loc"][0] == "body" for erro in erros)
    assert all(isinstance(erro["msg"], str) for erro in erros)
    assert all(isinstance(erro["type"], str) for erro in erros)

    resposta_sem_email = client.post(
        "/auth/login", json={"password": "senha-qualquer"}
    )
    assert resposta_sem_email.status_code == 422
    erros_sem_email = resposta_sem_email.json()["detail"]
    assert any(erro["loc"] == ["body", "email"] for erro in erros_sem_email)
