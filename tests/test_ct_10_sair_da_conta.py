def test_ct10_rotas_protegidas_nao_aceitam_sessao_sem_token(client):
    """CT-10: após sair, chamadas protegidas sem token devem ser recusadas.

    O logout da interface remove o token localmente; a API não tem rota de
    logout nem revogação de token, portanto este teste verifica a proteção
    que se aplica quando o cliente deixa de enviar o token.
    """
    resposta = client.get("/tasks")

    assert resposta.status_code == 401
