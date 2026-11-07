from uuid import uuid4

import pytest


SENHA = "SenhaSegura123"


def novo_email():
    return f"{uuid4().hex}@example.com"


def cadastrar(client, *, nome="Aluno Teste", email=None, senha=SENHA):
    email = email or novo_email()
    resposta = client.post(
        "/auth/register",
        json={"name": nome, "email": email, "password": senha},
    )
    return email, resposta


def autenticar(client, *, email=None, senha=SENHA):
    email = email or novo_email()
    _, cadastro = cadastrar(client, email=email, senha=senha)
    assert cadastro.status_code == 201, cadastro.text
    login = client.post("/auth/login", json={"email": email, "password": senha})
    assert login.status_code == 200, login.text
    token = login.json()["access_token"]
    return email, {"Authorization": f"Bearer {token}"}


# CT-01 — Login com senha incorreta
# A API deve rejeitar credenciais inválidas e não emitir token.
def test_ct01_login_rejeita_senha_incorreta(client):
    email, _ = cadastrar(client)

    resposta = client.post(
        "/auth/login", json={"email": email, "password": "SenhaErrada123"}
    )

    assert resposta.status_code == 401
    assert "access_token" not in resposta.json()


# CT-02 — Login com e-mail incorreto
# Usa e-mail válido no formato, mas que não foi cadastrado.
def test_ct02_login_rejeita_email_nao_cadastrado(client):
    resposta = client.post(
        "/auth/login",
        json={"email": novo_email(), "password": SENHA},
    )

    assert resposta.status_code == 401
    assert "access_token" not in resposta.json()


# CT-03 — Mostrar/ocultar senha
# Mostrar ou ocultar é comportamento visual do cliente e não pode ser validado
# por uma chamada HTTP. Este teste verifica o login que usa o campo de senha.
def test_ct03_login_aceita_senha_correta(client):
    email, _ = cadastrar(client)

    resposta = client.post(
        "/auth/login", json={"email": email, "password": SENHA}
    )

    assert resposta.status_code == 200
    assert resposta.json()["token_type"].lower() == "bearer"
    assert resposta.json()["access_token"]


# CT-04 — Cadastro sem campos obrigatórios
@pytest.mark.parametrize(
    "dados",
    [
        {"email": "aluno@example.com", "password": SENHA},
        {"name": "Aluno Teste", "password": SENHA},
        {"name": "Aluno Teste", "email": "aluno@example.com"},
    ],
    ids=["sem-nome", "sem-email", "sem-senha"],
)
def test_ct04_cadastro_rejeita_campo_obrigatorio_ausente(client, dados):
    resposta = client.post("/auth/register", json=dados)

    assert resposta.status_code == 422


# CT-05 — Cadastro exige senha com pelo menos oito caracteres
@pytest.mark.xfail(reason="BUG-01: a API aceita senhas de 6 ou 7 caracteres", strict=False)
@pytest.mark.parametrize("senha", ["123456", "1234567"], ids=["6-caracteres", "7-caracteres"])
def test_ct05_cadastro_rejeita_senha_com_menos_de_oito_caracteres(client, senha):
    resposta = client.post(
        "/auth/register",
        json={"name": "Aluno Teste", "email": novo_email(), "password": senha},
    )

    assert resposta.status_code == 422


# CT-06 — Criar tarefa com título válido e descrição opcional
# A criação exige autenticação; o título deve ter ao menos três caracteres.
def test_ct06_cria_tarefa_com_descricao_vazia(client):
    _, headers = autenticar(client)

    resposta = client.post(
        "/tasks", json={"title": "Minha tarefa"}, headers=headers
    )

    assert resposta.status_code == 201, resposta.text
    tarefa = resposta.json()
    assert tarefa["title"] == "Minha tarefa"
    assert tarefa["description"] is None
    assert tarefa["completed"] is False


# CT-07 — Visualizar tarefas, incluindo datas de criação e atualização
def test_ct07_lista_tarefas_com_datas(client):
    _, headers = autenticar(client)
    criada = client.post(
        "/tasks",
        json={"title": "Tarefa para listar", "description": "Descrição"},
        headers=headers,
    )
    assert criada.status_code == 201, criada.text

    resposta = client.get("/tasks", headers=headers)

    assert resposta.status_code == 200
    tarefa = next(item for item in resposta.json() if item["id"] == criada.json()["id"])
    assert tarefa["title"] == "Tarefa para listar"
    assert tarefa["description"] == "Descrição"
    assert tarefa["created_at"]
    assert tarefa["updated_at"]


# CT-08 — Editar título e descrição da tarefa
@pytest.mark.xfail(reason="BUG-05: a API n?o persiste a nova descri??o", strict=False)
def test_ct08_edita_titulo_e_descricao_da_tarefa(client):
    _, headers = autenticar(client)
    criada = client.post(
        "/tasks",
        json={"title": "Título original", "description": "Descrição original"},
        headers=headers,
    )
    assert criada.status_code == 201, criada.text

    resposta = client.put(
        f"/tasks/{criada.json()['id']}",
        json={"title": "Título atualizado", "description": "Nova descrição"},
        headers=headers,
    )

    assert resposta.status_code == 200, resposta.text
    assert resposta.json()["title"] == "Título atualizado"
    assert resposta.json()["description"] == "Nova descrição"


# CT-09 — Excluir tarefa
# A confirmação de exclusão é visual; aqui se verifica o efeito da confirmação,
# isto é, que a tarefa deixa de existir e não aparece mais na listagem.
@pytest.mark.xfail(reason="BUG-07: a API responde 204, mas mant?m a tarefa", strict=False)
def test_ct09_exclui_tarefa_e_remove_da_listagem(client):
    _, headers = autenticar(client)
    criada = client.post(
        "/tasks", json={"title": "Tarefa para excluir"}, headers=headers
    )
    assert criada.status_code == 201, criada.text
    tarefa_id = criada.json()["id"]

    exclusao = client.delete(f"/tasks/{tarefa_id}", headers=headers)

    assert exclusao.status_code == 204
    assert exclusao.content == b""
    assert client.get(f"/tasks/{tarefa_id}", headers=headers).status_code == 404
    ids = {item["id"] for item in client.get("/tasks", headers=headers).json()}
    assert tarefa_id not in ids


# CT-10 — Meu perfil
# A API permite consultar o perfil e alterar a senha. Não há rota para editar
# nome/e-mail; essa parte do requisito não pode ser coberta como funcionalidade.
def test_ct10_consulta_perfil_e_altera_senha(client):
    email, headers = autenticar(client)

    perfil = client.get("/users/me", headers=headers)
    assert perfil.status_code == 200
    assert perfil.json()["email"] == email
    assert perfil.json()["name"] == "Aluno Teste"

    alteracao = client.patch(
        "/users/me/password",
        json={"current_password": SENHA, "new_password": "NovaSenhaSegura123"},
        headers=headers,
    )
    assert alteracao.status_code == 200, alteracao.text

    novo_login = client.post(
        "/auth/login",
        json={"email": email, "password": "NovaSenhaSegura123"},
    )
    assert novo_login.status_code == 200, novo_login.text
