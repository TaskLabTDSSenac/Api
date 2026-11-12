"""CT-10 | Editar tarefa | Editar tarefa existente."""


import pytest


@pytest.mark.xfail(reason="TaskService.update_task atualiza apenas title; description permanece com o valor antigo.")
def test_ct10_editar_tarefa_persiste_valores_novos(client, headers_autenticados):
    """CT-10: a API deve persistir os novos valores da tarefa editada."""
    criada = client.post("/tasks", json={"title": "Tarefa antiga", "description": "DescriÃ§Ã£o antiga"}, headers=headers_autenticados)
    dados = {"title": "Tarefa CT-10 editada", "description": "DescriÃ§Ã£o nova"}

    resposta = client.put(f"/tasks/{criada.json()['id']}", json=dados, headers=headers_autenticados)
    leitura = client.get(f"/tasks/{criada.json()['id']}", headers=headers_autenticados)

    assert criada.status_code == 201
    assert resposta.status_code == 200
    assert leitura.status_code == 200
    assert leitura.json()["title"] == dados["title"]
    assert leitura.json()["description"] == dados["description"]

