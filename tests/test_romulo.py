def test_ct01_login_com_senha_incorreta(client):
    """CT-01: O sistema deve impedir o acesso e exibir mensagem informando credenciais inválidas.."""
    dados = {
        "name": "Aluno Teste",
        "email": "ct02@example.com",
        "password": "123456",
    }

    resposta = client.post("/auth/login", json=dados)

    assert resposta.status_code == 422

def test_ct02_cadastrar_usuario_com_dados_validos(client):
    # CT-02: a API deve permitir o cadastro de um usuário com dados válidos.    
    dados = {
        "name": "Toinho Teste",
        "email": "ct02@example.com",
        "password": "12345678",
    }

    resposta = client.post("/auth/register", json=dados)

    assert resposta.status_code == 201

def test_ct03_cadastrar_com_email_existente(client):
    # CT-03: a API deve rejeitar o cadastro de um usuário com email já existente.
    dados = {
        "name": "Toinho Teste",
        "email": "ct02@example.com",
        "password": "12345678",
    }

    resposta = client.post("/auth/register", json=dados)

    assert resposta.status_code == 409

def test_ct04_login_com_credenciais_validas(client):
    # CT-04: a API deve permitir o login com credenciais válidas.
    dados = {
        "email": "ct02@example.com",
        "password": "12345678",
    }

    resposta = client.post("/auth/login", json=dados)

    assert resposta.status_code == 200


def test_ct05_criacao_de_tarefas_com_titulo_e_descricao_validos(client):
    # CT-06: a API deve permitir a criação de tarefas com título e descrição válidos.
    login = client.post("/auth/login", json={
        "email": "ct02@example.com",
        "password": "12345678"
    })

    assert login.status_code == 200

    token = login.json()["access_token"]

    dados = {
        "title": "Tarefa de Teste",
        "description": "Descrição da tarefa de teste"
    }

    resposta = client.post(
        "/tasks",
        json=dados,
        headers={"Authorization": f"Bearer {token}"}
    )

    assert resposta.status_code == 201

def test_ct06_criacao_de_tarefas_com_titulo_muito_curto(client):
    # CT-06: a API deve rejeitar a criação de tarefas com título muito curto.
    login = client.post("/auth/login", json={
        "email": "ct02@example.com",
        "password": "12345678"
    })

    assert login.status_code == 200

    token = login.json()["access_token"]

    dados = {
        "title": "ab",
        "description": "Descrição da tarefa de teste"
    }

    resposta = client.post(
        "/tasks",
        json=dados,
        headers={"Authorization": f"Bearer {token}"}
    )

    assert resposta.status_code == 422

def test_ct07_listar_tarefas(client):
    # CT-07: a API deve permitir listar as tarefas do usuário autenticado.
     login = client.post("/auth/login", json={
            "email": "ct02@example.com",
            "password": "12345678"
        })
     token = login.json()["access_token"]

     resposta = client.get(
         "/tasks",
         headers={"Authorization": f"Bearer {token}"}
     )

     assert resposta.status_code == 200

def test_ct08_alterar_titulo_e_descricao_de_tarefa(client):
    # CT-08: a API deve permitir alterar o título e a descrição de uma tarefa existente.
    login = client.post("/auth/login", json={
        "email": "ct02@example.com",
        "password": "12345678"
    })

    assert login.status_code == 200

    token = login.json()["access_token"]

    # Criar uma tarefa para testar a alteração
    dados_tarefa = {
        "title": "Tarefa de Teste",
        "description": "Descrição da tarefa de teste"
    }

    resposta_tarefa = client.post(
        "/tasks",
        json=dados_tarefa,
        headers={"Authorization": f"Bearer {token}"}
    )

    assert resposta_tarefa.status_code == 201

    tarefa_id = resposta_tarefa.json()["id"]

    # Alterar o título e a descrição da tarefa
    dados_alteracao = {
        "title": "Tarefa de Teste - Alterada",
        "description": "Descrição da tarefa de teste - Alterada"
    }

    resposta_alteracao = client.put(
        f"/tasks/{tarefa_id}",
        json=dados_alteracao,
        headers={"Authorization": f"Bearer {token}"}
    )

    assert resposta_alteracao.status_code == 200

def test_ct09_marcar_tarefa_como_concluida(client):
    # CT-09: a API deve permitir marcar uma tarefa como concluída.
    login = client.post("/auth/login", json={
        "email": "ct02@example.com",
        "password": "12345678"
    })

    assert login.status_code == 200

    token = login.json()["access_token"]

    dados_tarefa = {
        "title": "Tarefa de Teste",
        "description": "Descrição da tarefa de teste"
    }

    resposta_tarefa = client.post(
        "/tasks",
        json=dados_tarefa,
        headers={"Authorization": f"Bearer {token}"}
    )

    assert resposta_tarefa.status_code == 201

    tarefa_id = resposta_tarefa.json()["id"]

    resposta_conclusao = client.patch(
        f"/tasks/{tarefa_id}/complete",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert resposta_conclusao.status_code == 200
    assert resposta_conclusao.json()["completed"] is True

def test_ct10_excluir_tarefa(client):
    # CT-10: a API deve permitir excluir uma tarefa existente.
    login = client.post("/auth/login", json={
        "email": "ct02@example.com",
        "password": "12345678"
    })

    assert login.status_code == 200

    token = login.json()["access_token"]

    # Criar uma tarefa para testar a exclusão
    dados_tarefa = {
        "title": "Tarefa de Teste",
        "description": "Descrição da tarefa de teste"
    }

    resposta_tarefa = client.post(
        "/tasks",
        json=dados_tarefa,
        headers={"Authorization": f"Bearer {token}"}
    )

    assert resposta_tarefa.status_code == 201

    tarefa_id = resposta_tarefa.json()["id"]

    # Excluir a tarefa
    resposta_exclusao = client.delete(
        f"/tasks/{tarefa_id}",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert resposta_exclusao.status_code == 204