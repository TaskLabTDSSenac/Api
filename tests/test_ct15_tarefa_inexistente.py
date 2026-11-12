"""CT-15 | Tarefas | Excluir tarefa inexistente."""


def test_ct15_excluir_tarefa_inexistente_retorna_404(client, headers_autenticados):
    """CT-15: a API deve retornar 404 ao excluir tarefa inexistente."""
    resposta = client.delete("/tasks/999999", headers=headers_autenticados)

    assert resposta.status_code == 404
    assert resposta.json()["detail"]
