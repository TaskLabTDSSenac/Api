def test_ct03_cadastro_rejeita_confirmacao_de_senha_diferente(client):
    """CT-03: a API deve rejeitar o campo extra de confirmação de senha."""
    dados = {
        "name": "Thiago Teste",
        "email": "ct03@example.com",
        "password": "12345678",
        "confirm_password": "87654321",
    }

    resposta = client.post("/auth/register", json=dados)

    assert resposta.status_code == 422
