"""CT-11 | Cadastro | Rejeitar e-mail duplicado."""


def test_ct11_cadastro_rejeita_email_duplicado(client, usuario_cadastrado):
    """CT-11: a API deve rejeitar cadastro com e-mail já existente."""
    dados = {"name": "Outro Aluno", "email": usuario_cadastrado["email"], "password": "OutraSenha123!"}

    resposta = client.post("/auth/register", json=dados)

    assert resposta.status_code == 409
    assert resposta.json()["detail"]
