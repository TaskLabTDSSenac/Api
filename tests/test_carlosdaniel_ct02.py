def test_ct02_cadastro_de_usuario_retorna_dados_publicos(client):
    """CT-02: cadastro válido deve criar a conta e retornar HTTP 201."""
    dados = {
        "name": "Carlos Daniel CT02",
        "email": "carlosdaniel.ct02@example.com",
        "password": "SenhaValida123",
    }

    resposta = client.post("/auth/register", json=dados)

    assert resposta.status_code == 201
    usuario = resposta.json()
    assert usuario["id"] > 0
    assert usuario["name"] == dados["name"]
    assert usuario["email"] == dados["email"]
    assert set(usuario) == {"id", "name", "email"}


def test_ct02_cadastro_sem_nome_retorna_erro_de_validacao(client):
    """CT-02: cadastro sem o nome obrigatório deve retornar HTTP 422."""
    resposta = client.post(
        "/auth/register",
        json={"email": "carlosdaniel.ct02-sem-nome@example.com", "password": "SenhaValida123"},
    )

    assert resposta.status_code == 422
    erros = resposta.json()["detail"]
    erro_nome = next(erro for erro in erros if erro["loc"][-1] == "name")
    assert erro_nome["loc"] == ["body", "name"]
    assert isinstance(erro_nome["msg"], str)
    assert isinstance(erro_nome["type"], str)
