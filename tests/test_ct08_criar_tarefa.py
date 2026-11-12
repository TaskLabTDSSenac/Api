"""CT-08 | Criar tarefa | Criar tarefa com t?tulo e descri??o."""


def test_ct08_criar_tarefa_salva_titulo_e_descricao(client, headers_autenticados):
    """CT-08: a API deve salvar a tarefa e exibi-la na listagem."""
    dados = {"title": "Tarefa CT-08", "description": "Descrição enviada no CT-08"}

    resposta = client.post("/tasks", json=dados, headers=headers_autenticados)
    listagem = client.get("/tasks", headers=headers_autenticados)

    assert resposta.status_code == 201
    assert resposta.json()["title"] == dados["title"]
    assert resposta.json()["description"] == dados["description"]
    assert any(t["title"] == dados["title"] and t["description"] == dados["description"] for t in listagem.json())
