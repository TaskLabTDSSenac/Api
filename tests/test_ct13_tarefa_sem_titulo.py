"""CT-13 | Tarefas | Rejeitar tarefa sem t?tulo."""


def test_ct13_criar_tarefa_sem_titulo_retorna_erro_de_validacao(client, headers_autenticados):
    """CT-13: a API deve rejeitar tarefa sem título."""
    dados = {"description": "Sem título"}

    resposta = client.post("/tasks", json=dados, headers=headers_autenticados)

    assert resposta.status_code == 422
    assert any(erro["loc"][-1] == "title" for erro in resposta.json()["detail"])
