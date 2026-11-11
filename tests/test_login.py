def test_ct03_Cadastrar_novo_usuário_com_dados_válidos(client):
    """CT-02: a API Cadastrar novo usuário com dados válidos."""
    dados = {
        "name": "maria",
        "email": "maria@teste.com",
        "password": "Teste@123",
    }

    resposta = client.post("/auth/register", json=dados)

    assert resposta.status_code == 201

def test_ct02_login_sistema_autentica_o_usuário_com_sucesso_e_redireciona_para_a_lista_de_tarefas(client):
    """CT-02: O sistema autentica o usuário com sucesso e redireciona para a lista de tarefas."""
    
    dados2 = {
  "email": "maria@teste.com",
  "password": "Teste@123"
}
    resposta2 = client.post("/auth/login", json=dados2)

    assert resposta2.status_code == 200

def test_ct03_Realizar_login_com_credenciais_válidas(client):
    """CT-02: a API Realiza login com credenciais válidas."""
    dados3 = {
        
        "email": "maria@teste.com",
        "password": "Teste@123",
      
}

    resposta3 = client.post("/auth/login", json=dados3)

    assert resposta3.status_code == 200


def test_ct03_Tentar_login_com_senha_incorreta(client):
    """CT-02: a API Tentar login com senha incorreta."""
    dados4 = {
        
        "email": "maria@teste.com",
        "password": "Errada@123",
      
}

    resposta4 = client.post("/auth/login", json=dados4)

    assert resposta4.status_code == 401

def test_ct03_Tentar_login_com_campos_de_email_e_senha_vazios(client):
    """CT-02: a API Tentar login com campos de e-mail e senha vazios."""
    dados5 = {
        
        "email": "",
        "password": "",
      
}

    resposta5 = client.post("/auth/login", json=dados5)

    assert resposta5.status_code == 422

def _criar_tarefa_para_teste(client, email):
    cadastro = client.post(
        "/auth/register",
        json={"name": "Aluno Teste", "email": email, "password": "Teste@123"},
    )
    assert cadastro.status_code == 201

    login = client.post(
        "/auth/login",
        json={"email": email, "password": "Teste@123"},
    )
    assert login.status_code == 200

    token = login.json().get("access_token") or login.json().get("token")
    assert token
    headers = {"Authorization": f"Bearer {token}"}
    tarefa = client.post(
        "/tasks",
        json={"title": "Estudar UC11", "description": "Preparar atividade"},
        headers=headers,
    )
    assert tarefa.status_code == 201
    return tarefa.json(), headers


def test_ct07_editar_tarefa(client):
    """CT-07: editar tarefa existente e verificar o título atualizado."""
    tarefa, headers = _criar_tarefa_para_teste(client, "ct07@example.com")

    resposta = client.put(
        f"/tasks/{tarefa['id']}",
        json={"title": "Estudar UC12", "description": "Preparar atividade"},
        headers=headers,
    )

    assert resposta.status_code == 200
    assert resposta.json()["title"] == "Estudar UC12"
    lista = client.get("/tasks", headers=headers)
    assert lista.status_code == 200
    assert any(item["id"] == tarefa["id"] and item["title"] == "Estudar UC12" for item in lista.json())


def test_ct08_concluir_tarefa(client):
    """CT-08: marcar tarefa como concluída."""
    tarefa, headers = _criar_tarefa_para_teste(client, "ct08@example.com")

    resposta = client.patch(f"/tasks/{tarefa['id']}/complete", headers=headers)

    assert resposta.status_code == 200
    assert resposta.json()["completed"] is True


def test_ct09_excluir_tarefa(client):
    """CT-09: excluir tarefa e confirmar sua remoção da lista."""
    tarefa, headers = _criar_tarefa_para_teste(client, "ct09@example.com")

    resposta = client.delete(f"/tasks/{tarefa['id']}", headers=headers)

    assert resposta.status_code == 204
    lista = client.get("/tasks", headers=headers)
    assert lista.status_code == 200
    assert all(item["id"] != tarefa["id"] for item in lista.json())


def _criar_headers_perfil(client, email):
    client.post(
        "/auth/register",
        json={"name": "Usuario Locust", "email": email, "password": "Teste@123"},
    )
    login = client.post(
        "/auth/login",
        json={"email": email, "password": "Teste@123"},
    )
    token = login.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_consultar_perfil_com_token_valido(client):
    headers = _criar_headers_perfil(client, "perfil_locust@example.com")

    resposta = client.get("/users/me", headers=headers)

    assert resposta.status_code == 200
    assert resposta.json()["email"] == "perfil_locust@example.com"


def test_consultar_perfil_sem_token(client):
    resposta = client.get("/users/me")

    assert resposta.status_code == 401


def test_consultar_perfil_com_token_invalido(client):
    resposta = client.get(
        "/users/me",
        headers={"Authorization": "Bearer token-invalido"},
    )

    assert resposta.status_code == 401
