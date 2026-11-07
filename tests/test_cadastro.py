import pytest

@pytest.mark.xfail(reason="BUG-01: a API aceita senhas de 6 ou 7 caracteres", strict=False)
def test_ct05_cadastro_rejeita_senha_menor_que_oito_caracteres(client):
    """CT-02: a API deve rejeitar uma senha de apenas 6 caracteres."""
    dados = {
        "name": "Aluno Teste",
        "email": "ct02@example.com",
        "password": "123456",
    }

    resposta = client.post("/auth/register", json=dados)

    assert resposta.status_code == 422

def test_ct03_login(client):
    """CT-03: login com sucesso"""
    dados = {
        "email": "ct02@example.com",
        "password": "123456",
    }

    resposta = client.post("/auth/login", json=dados)

    assert resposta.status_code == 200