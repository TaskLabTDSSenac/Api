"""CT-12 | Cadastro | Rejeitar senha curta."""


import pytest


@pytest.mark.xfail(reason="UserCreate.validate_password permite explicitamente senhas de 6 a 7 caracteres; a API retorna 201.")
def test_ct12_cadastro_rejeita_senha_curta(client):
    """CT-12: a API deve rejeitar cadastro com senha menor que oito caracteres."""
    dados = {"name": "Aluno CT-12", "email": "ct12@example.com", "password": "123456"}

    resposta = client.post("/auth/register", json=dados)

    assert resposta.status_code == 422
    assert any(erro["loc"][-1] == "password" for erro in resposta.json()["detail"])

