def test_usuario_edita_missao_salva(client, usuario_autenticado, missao_criada):
    resposta = client.put(
        f"/tasks/{missao_criada['id']}",
        headers=usuario_autenticado["headers"],
        json={"title": "Missão atualizada", "description": "Descrição atualizada"},
    )

    assert resposta.status_code == 200
    assert resposta.json()["title"] == "Missão atualizada"
    assert resposta.json()["description"] == "Descrição atualizada"

    consulta = client.get(
        f"/tasks/{missao_criada['id']}", headers=usuario_autenticado["headers"]
    )
    assert consulta.status_code == 200
    assert consulta.json()["title"] == "Missão atualizada"
