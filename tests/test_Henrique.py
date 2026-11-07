def test_ct01_login_EntrarComSenhaIncorreta(client):
    """CT-01: O sistema deve rejeitar o login e exibir mensagem de erro."""
    dados = {
        "email": "Carlos.Henrique@gmail.com",
        "password": "8436",
    }

    resposta = client.post("/auth/login", json=dados)

    assert resposta.status_code == 401



def test_ct02_login_Entrar_sem_senha_e_email(client):
    """CT-02: O sistema deve rejeitar o login e exibir mensagem de erro."""
    dados = {
        "email": "",
        "password": "",
    }

    resposta = client.post("/auth/login", json=dados)

    assert resposta.status_code == 422



def test_ct03_register_Cadastro_sem_senha_e_email(client):
    """CT-03: O sistema deve rejeitar o Cadastro e exibir mensagem de erro."""
    dados = {
        "email": "",
        "password": "",
    }

    resposta = client.post("/auth/register", json=dados)

    assert resposta.status_code == 422



def test_ct04_login_Cadastro_com_senha_incorreta(client):
    """CT-04: O sistema deve rejeitar o Cadastro e exibir mensagem de erro."""
    dados = {
        "email": "CarllosBlack@gamil.com",
        "password": "bgdt",
        "name": "Henrique",
    }

    resposta = client.post("/auth/register", json=dados)

    assert resposta.status_code == 422



def test_ct05_login_Entrar_com_senha_correta(client):
    """CT-05: O sistema deve aprovar o Login e entrar na conta do usuario."""

    dados2 = {
        "email": "Carlos.Henrique@gmail.com",
        "password": "CarlosSantos",
        "name": "Henrique",
    }

    resposta2 = client.post("/auth/register", json=dados2)


    dados = {
        "email": "Carlos.Henrique@gmail.com",
        "password": "CarlosSantos",
    }

    resposta = client.post("/auth/login", json=dados)

    assert resposta.status_code == 200



def test_ct06_login_Entrar_com_email_correto(client):
    """CT-06: O sistema deve aprovar o login e entrar na conta do usuario."""
    dados = {
        "email": "Carlos.Henrique@gmail.com",
        "password": "CarlosSantos",
    }

    resposta = client.post("/auth/login", json=dados)

    assert resposta.status_code == 200



def test_ct07_Cadastro_Cadastro_com_email_incorreto(client):
    """CT-07: O sistema deve rejeitar o cadastro e exibir mensagem de erro."""
    dados = {
        "email": "CarllosBlackgamil.com",
        "password": "bgdt",
        "name": "Henrique",
    }

    resposta = client.post("/auth/register", json=dados)

    assert resposta.status_code == 422



def test_ct08_criar_tarefa_com_caracters_além_do_limite(client, auth_headers):
    """CT-08: O sistema deve rejeitar a criação de tarefa e exibir mensagem de erro."""
    dados2 = {
        "email": "Carlos.Henrique@gmail.com",
        "password": "CarlosSantos",
    }

    resposta2 = client.post("/auth/login", json=dados2)
    token = resposta2.json()["access_token"]

    dados = {
        "title": "Título",
        "description": "yygyhujhuhygytgfuiadsfajdehgaddshhjhjhjhjhjhghgfjkgjkgjkgkjfkjgkjgjkgfhjfsdfjhsjjhgjjgjsgjfdgfsgdhhhhyjyygyhujhuhygytgfuiadsfajdehgaddshhjhjhjhjhjhghgfjkgjkgjkgkjfkjgkjgjkgfhjfsdfjhsjjhgjjgjsgjfdgfsgdhhhhyjyygyhujhuhygytgfuiadsfajdehgaddshhjhjhjhjhjhghgfjkgjkgjkgkjfkjgkjgjkgfhjfsdfjhsjjhgjjgjsgjfdgfsgdhhhhyjyygyhujhuhygytgfuiadsfajdehgaddshhjhjhjhjhjhghgfjkgjkgjkgkjfkjgkjgjkgfhjfsdfjhsjjhgjjgjsgjfdgfsgdhhhhyjyygyhujhuhygytgfuiadsfajdehgaddshhjhjhjhjhjhghgfjkgjkgjkgkjfkjgkjgjkgfhjfsdfjhsjjhgjjgjsgjfdgfsgdhhhhyjyygyhujhuhygytgfuiadsfajdehgaddshhjhjhjhjhjhghgfjkgjkgjkgkjfkjgkjgjkgfhjfsdfjhsjjhgjjgjsgjfdgfsgdhhhhyj"
    }

    resposta = client.post("/tasks", json=dados, headers={"Authorization": f"Bearer {token}"})

    assert resposta.status_code == 201



def test_ct09_criar_tarefa_Criação_de_tarefas_sem_titulo(client, auth_headers):
    """CT-09: O sistema deve rejeitar a criação de tarefa e exibir mensagem de erro."""
    dados2 = {
        "email": "Carlos.Henrique@gmail.com",
        "password": "CarlosSantos",
    }

    resposta2 = client.post("/auth/login", json=dados2)
    token = resposta2.json()["access_token"]

    dados = {
        "title": "",
        "description": "ovo branco e lisinho"
    }

    resposta = client.post("/tasks", json=dados, headers={"Authorization": f"Bearer {token}"})

    assert resposta.status_code == 422



def test_ct10_editar_descrição_de_tarefa_Edição_de_descrição_de_tarefa(client, auth_headers):
    """CT-10: O sistema deve aprovar a edição de tarefa e voltar pra a tela inicial."""
    dados2 = {
        "email": "Carlos.Henrique@gmail.com",
        "password": "CarlosSantos",
    }

    resposta2 = client.post("/auth/login", json=dados2)
    token = resposta2.json()["access_token"]

    dados = {
        "title": "Título",
        "description": "descrição"
    }

    resposta = client.post("/tasks", json=dados, headers={"Authorization": f"Bearer {token}"})

    dados3 = {
        "title": "Título",
        "description": "descrição"
    }

    id = str(resposta.json()["id"])
    resposta3 = client.put("/tasks/"+id, json=dados3, headers={"Authorization": f"Bearer {token}"})

    assert resposta3.status_code == 200