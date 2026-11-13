def test_cadastro_valido_retorna_dados_publicos(client):
    """A API deve cadastrar o usuário sem expor senha ou hash."""
    dados = {
        "name": "Aluno Teste",
        "email": "cadastro-valido@example.com",
        "password": "SenhaValida123!",
    }

    resposta = client.post("/auth/register", json=dados)

    assert resposta.status_code == 201
    assert resposta.json()["email"] == dados["email"]
    assert "password" not in resposta.json()
    assert "password_hash" not in resposta.json()
