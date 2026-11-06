from uuid import uuid4

def test_cadastro_de_novo_usuario(client):
    email = f"kauane.{uuid4().hex}@example.com"
    resposta = client.post(
        "/auth/register",
        json={"name": "Nova Usuária", "email": email, "password": "SenhaValida123"},
    )

    assert resposta.status_code == 201
    assert resposta.json()["email"] == email
