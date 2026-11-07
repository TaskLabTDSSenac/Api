def test_ct02_cadastro_rejeita_confirmacao_de_senha_ausente(client):
    """CT-02: o cadastro deve exigir a confirmação da senha.

    A API atual não oferece um campo de confirmação; este caso registra a
    validação esperada para quando o cliente enviar password_confirmation.
    """
    resposta = client.post("/auth/register", json={
        "name": "CT02",
        "email": "ct02@example.com",
        "password": "SenhaValida123",
        "password_confirmation": "SenhaValida123",
    })

   
    assert resposta.status_code == 422
