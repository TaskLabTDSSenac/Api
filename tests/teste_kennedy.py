def test_login_rejeita_senha_incorreta(client):
    """Login com senha incorreta deve retornar erro de autenticação."""
    cadastro = {
        "name": "Aluno Teste",
        "email": "kennedy.login@example.com",
        "password": "SenhaCorreta123",
    }
    resposta_cadastro = client.post("/auth/register", json=cadastro)
    assert resposta_cadastro.status_code == 201

    resposta_login = client.post(
        "/auth/login",
        json={"email": cadastro["email"], "password": "SenhaErrada123"},
    )

    assert resposta_login.status_code == 401
    assert resposta_login.json() == {"detail": "E-mail ou senha inválidos."}


def test_login_com_credenciais_validas(client):
    """Login com credenciais válidas deve retornar um token de acesso."""
    cadastro = {
        "name": "Aluno Teste",
        "email": "kennedy.valido@example.com",
        "password": "SenhaCorreta123",
    }
    resposta_cadastro = client.post("/auth/register", json=cadastro)
    assert resposta_cadastro.status_code == 201

    resposta_login = client.post(
        "/auth/login",
        json={"email": cadastro["email"], "password": cadastro["password"]},
    )

    assert resposta_login.status_code == 200
    dados_login = resposta_login.json()
    assert dados_login["access_token"]
    assert dados_login["token_type"] == "bearer"


def test_cadastro_de_novo_usuario_valido(client):
    """Um novo usuário deve ser cadastrado com sucesso."""
    resposta = client.post(
        "/auth/register",
        json={
            "name": "Novo Aluno",
            "email": "kennedy.novo@example.com",
            "password": "SenhaSegura123",
        },
    )

    assert resposta.status_code == 201
    assert resposta.json()["email"] == "kennedy.novo@example.com"


def test_cadastro_rejeita_email_ja_cadastrado(client):
    """Não deve ser possível cadastrar o mesmo e-mail duas vezes."""
    dados = {
        "name": "Aluno Teste",
        "email": "kennedy.duplicado@example.com",
        "password": "SenhaSegura123",
    }
    primeira_resposta = client.post("/auth/register", json=dados)
    assert primeira_resposta.status_code == 201

    resposta_duplicada = client.post("/auth/register", json=dados)

    assert resposta_duplicada.status_code == 409
    assert resposta_duplicada.json() == {"detail": "E-mail já cadastrado."}


def _criar_usuario_e_obter_token(client):
    cadastro = {
        "name": "Aluno Tarefas",
        "email": "kennedy.tarefas@example.com",
        "password": "SenhaSegura123",
    }
    resposta_cadastro = client.post("/auth/register", json=cadastro)
    assert resposta_cadastro.status_code == 201

    resposta_login = client.post(
        "/auth/login",
        json={"email": cadastro["email"], "password": cadastro["password"]},
    )
    assert resposta_login.status_code == 200
    return resposta_login.json()["access_token"]


def test_criar_nova_tarefa_com_dados_validos(client):
    """Usuário autenticado deve conseguir criar e listar uma tarefa."""
    token = _criar_usuario_e_obter_token(client)
    headers = {"Authorization": f"Bearer {token}"}

    resposta = client.post(
        "/tasks",
        json={"title": "Estudar testes", "description": "Revisar cenários da API"},
        headers=headers,
    )

    assert resposta.status_code == 201
    assert resposta.json()["title"] == "Estudar testes"
    assert resposta.json()["description"] == "Revisar cenários da API"

    resposta_lista = client.get("/tasks", headers=headers)
    assert resposta_lista.status_code == 200
    assert any(tarefa["id"] == resposta.json()["id"] for tarefa in resposta_lista.json())


def test_criar_tarefa_sem_titulo_e_rejeitado(client):
    """A API deve rejeitar tarefa sem o campo obrigatório título."""
    token = _criar_usuario_e_obter_token(client)
    headers = {"Authorization": f"Bearer {token}"}

    resposta = client.post(
        "/tasks",
        json={"title": "", "description": "Descrição preenchida"},
        headers=headers,
    )

    assert resposta.status_code == 422
    resposta_lista = client.get("/tasks", headers=headers)
    assert resposta_lista.status_code == 200
    assert resposta_lista.json() == []
