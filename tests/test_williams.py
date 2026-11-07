
def test_ct11_rejeitar_email_invalido_do_usuario(client):
    """ct11: a API deve rejeitar um e-mail inválido do usuário."""
    dados = {
        "name": "Aluno Teste",
        "email": "ct11gmail.com",
        "password": "SenhaSegura123",
        "description": "Aluno de teste",
    }

    resposta = client.post("/auth/register", json=dados)

    assert resposta.status_code == 422

def test_ct12_cadastro_rejeita_nome_ausente(client):
    """ct12: a API deve rejeitar o cadastro de um usuário sem nome."""
    dados = {
        "email": "teste@gmail.com",
        "password": "SenhaSegura123",
        "description": "Aluno de teste",
    }

    resposta = client.post("/auth/register", json=dados)

    assert resposta.status_code == 422

def test_ct13_login_senha_errada(client):
    client.post("/auth/register", json={
        "name": "Aluno", "email": "aluno@example.com", "password": "Senha1234"
    })
    resposta = client.post("/auth/login", json={
        "email": "aluno@example.com", "password": "errada"
    })

    assert "access_token" not in resposta.json()