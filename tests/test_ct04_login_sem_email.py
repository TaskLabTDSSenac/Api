"""CT-04 | Login | Entrar sem e-mail."""


def test_ct04_login_sem_email_retorna_erro_de_validacao(client):
    """CT-04: a API deve informar que o e-mail é obrigatório quando ele não é enviado."""
    dados = {"password": "SenhaInicial123!"}

    resposta = client.post("/auth/login", json=dados)

    assert resposta.status_code == 422
    assert any(erro["loc"][-1] == "email" for erro in resposta.json()["detail"])
