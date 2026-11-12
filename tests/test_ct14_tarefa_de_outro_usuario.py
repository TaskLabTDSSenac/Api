"""CT-14 | Tarefas | Isolar tarefas por usu?rio."""


def test_ct14_usuario_nao_acessa_tarefa_de_outro_usuario(client, headers_autenticados):
    """CT-14: a API deve ocultar tarefa pertencente a outro usuÃ¡rio."""
    segunda = {"name": "Outro UsuÃ¡rio", "email": "ct14-outro@example.com", "password": "SenhaInicial123!"}
    cadastro = client.post("/auth/register", json=segunda)
    login = client.post("/auth/login", json={"email": segunda["email"], "password": segunda["password"]})
    headers_segundo = {"Authorization": f"Bearer {login.json()['access_token']}"}
    tarefa = client.post("/tasks", json={"title": "Tarefa privada"}, headers=headers_segundo)

    resposta = client.get(f"/tasks/{tarefa.json()['id']}", headers=headers_autenticados)

    assert cadastro.status_code == 201
    assert login.status_code == 200
    assert tarefa.status_code == 201
    assert resposta.status_code == 404
    assert resposta.json()["detail"]

