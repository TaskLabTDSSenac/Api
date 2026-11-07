def test_ct07_login_aceita_senha_informada(client):
    """CT-07: valida o envio da senha no login pela API.

    Mostrar/ocultar a senha pelo ícone é comportamento do frontend, que não
    está presente neste repositório; a API recebe apenas o valor informado.
    """
    client.post("/auth/register", json={
        "name": "CT07",
        "email": "ct07@example.com",
        "password": "SenhaValida123",
    })

    resposta = client.post("/auth/login", json={
        "email": "ct07@example.com",
        "password": "SenhaValida123",
    })

    assert resposta.status_code == 200
    assert resposta.json()["access_token"]
