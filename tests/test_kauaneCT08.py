def test_usuario_apaga_missao_salva(client, usuario_autenticado, missao_criada):
    resposta = client.delete(
        f"/tasks/{missao_criada['id']}", headers=usuario_autenticado["headers"]
    )

    assert resposta.status_code == 204
    assert resposta.content == b""

    consulta = client.get(
        f"/tasks/{missao_criada['id']}", headers=usuario_autenticado["headers"]
    )
    assert consulta.status_code == 404
