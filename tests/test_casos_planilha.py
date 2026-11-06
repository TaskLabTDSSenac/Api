import uuid

import pytest


def _criar_usuario(client):
    identificador = uuid.uuid4().hex
    dados = {
        "name": "Usuário de Teste",
        "email": f"{identificador}@example.com",
        "password": "SenhaSegura123",
    }
    resposta = client.post("/auth/register", json=dados)
    assert resposta.status_code == 201
    return dados


def _autenticar(client):
    usuario = _criar_usuario(client)
    resposta = client.post(
        "/auth/login",
        json={"email": usuario["email"], "password": usuario["password"]},
    )
    assert resposta.status_code == 200
    return {"Authorization": f"Bearer {resposta.json()['access_token']}"}


def test_ct02_login_rejeita_senha_incorreta(client):
    """CT-02: credenciais inválidas devem impedir o acesso."""
    usuario = _criar_usuario(client)

    resposta = client.post(
        "/auth/login",
        json={"email": usuario["email"], "password": "SenhaErrada123"},
    )

    assert resposta.status_code == 401
    assert resposta.json()["detail"] == "E-mail ou senha inválidos."


def test_ct03_login_rejeita_campos_obrigatorios_vazios(client):
    """CT-03: login não deve prosseguir com e-mail e senha em branco."""
    resposta = client.post("/auth/login", json={"email": "", "password": ""})

    assert resposta.status_code == 422


def test_ct04_visualizacao_de_senha(client):
    """CT-04: alternar a visibilidade da senha depende da interface gráfica."""
    pytest.skip("Caso de interface: este projeto contém somente a API, sem tela de login.")


def test_ct05_navegacao_para_tela_de_cadastro(client):
    """CT-05: validar o link e o redirecionamento exige a interface gráfica."""
    pytest.skip("Caso de interface: este projeto contém somente a API, sem tela de login/cadastro.")


def test_ct06_criacao_de_nova_tarefa(client):
    """CT-06: tarefa criada deve aparecer na listagem do usuário autenticado."""
    headers = _autenticar(client)
    dados = {"title": "Tarefa CT-06", "description": "Descrição inicial"}

    resposta = client.post("/tasks", json=dados, headers=headers)

    assert resposta.status_code == 201
    tarefa = resposta.json()
    assert tarefa["title"] == dados["title"]
    assert tarefa["description"] == dados["description"]
    assert tarefa["completed"] is False

    listagem = client.get("/tasks", headers=headers)
    assert listagem.status_code == 200
    assert any(item["id"] == tarefa["id"] for item in listagem.json())


def test_ct07_edicao_de_tarefa_existente(client):
    """CT-07: alterações da tarefa devem ser salvas e refletidas na listagem."""
    headers = _autenticar(client)
    criacao = client.post(
        "/tasks",
        json={"title": "Tarefa original", "description": "Descrição original"},
        headers=headers,
    )
    assert criacao.status_code == 201
    tarefa_id = criacao.json()["id"]
    dados_atualizados = {
        "title": "Tarefa atualizada",
        "description": "Descrição atualizada",
    }

    resposta = client.put(
        f"/tasks/{tarefa_id}", json=dados_atualizados, headers=headers
    )

    assert resposta.status_code == 200
    assert resposta.json()["title"] == dados_atualizados["title"]
    assert resposta.json()["description"] == dados_atualizados["description"]

    listagem = client.get("/tasks", headers=headers)
    tarefa_listada = next(item for item in listagem.json() if item["id"] == tarefa_id)
    assert tarefa_listada["title"] == dados_atualizados["title"]
    assert tarefa_listada["description"] == dados_atualizados["description"]


def test_ct08_conclusao_de_tarefa(client):
    """CT-08: concluir a tarefa deve atualizar seu estado para concluído."""
    headers = _autenticar(client)
    criacao = client.post(
        "/tasks",
        json={"title": "Tarefa para concluir", "description": "Teste CT-08"},
        headers=headers,
    )
    assert criacao.status_code == 201
    tarefa_id = criacao.json()["id"]

    resposta = client.patch(f"/tasks/{tarefa_id}/complete", headers=headers)

    assert resposta.status_code == 200
    assert resposta.json()["completed"] is True


def test_ct09_exclusao_de_tarefa(client):
    """CT-09: tarefa excluída deve sumir da listagem e não ser consultável."""
    headers = _autenticar(client)
    criacao = client.post(
        "/tasks",
        json={"title": "Tarefa para excluir", "description": "Teste CT-09"},
        headers=headers,
    )
    assert criacao.status_code == 201
    tarefa_id = criacao.json()["id"]

    resposta = client.delete(f"/tasks/{tarefa_id}", headers=headers)

    assert resposta.status_code == 204
    listagem = client.get("/tasks", headers=headers)
    assert listagem.status_code == 200
    assert all(item["id"] != tarefa_id for item in listagem.json())
    consulta = client.get(f"/tasks/{tarefa_id}", headers=headers)
    assert consulta.status_code == 404


def test_ct10_encerramento_de_sessao(client):
    """CT-10: logout e redirecionamento dependem do cliente e de suporte de logout."""
    pytest.skip(
        "A API não oferece endpoint para revogar token/logout; limpar o token e "
        "redirecionar para login depende da interface cliente."
    )


def test_ct11_cadastro_rejeita_email_com_formato_invalido(client):
    """CT-11: e-mail inválido deve impedir a conclusão do cadastro."""
    resposta = client.post(
        "/auth/register",
        json={
            "name": "Usuário de Teste",
            "email": "joao.teste.com",
            "password": "SenhaSegura123",
        },
    )

    assert resposta.status_code == 422
    assert any(
        erro["loc"] == ["body", "email"]
        for erro in resposta.json()["detail"]
    )
