def test_carlosdaniel_cadastro_normaliza_nome_e_email(client):
    """O cadastro deve aparar o nome e normalizar o e-mail retornado."""
    dados = {
        "name": "  Carlos Daniel  ",
        "email": "  Carlos.Daniel.Normalizacao@example.com  ",
        "password": "SenhaValida123",
    }

    resposta = client.post("/auth/register", json=dados)

    assert resposta.status_code == 201
    assert resposta.json()["name"] == "Carlos Daniel"
    assert resposta.json()["email"] == "carlos.daniel.normalizacao@example.com"
