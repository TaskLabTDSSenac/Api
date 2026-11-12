"""CT-03 | Login | Entrar sem a senha."""


def test_ct03_login_sem_senha_retorna_erro_de_validacao(client, usuario_cadastrado):
    """CT-03: a API deve informar que a senha é obrigatória quando ela não é enviada."""
    dados = {"email": usuario_cadastrado["email"]}

    resposta = client.post("/auth/login", json=dados)

    assert resposta.status_code == 422
    assert any(erro["loc"][-1] == "password" for erro in resposta.json()["detail"])
