import secrets

import pytest
from fastapi.testclient import TestClient


@pytest.fixture(scope="session")
def application(tmp_path_factory):
    # Configure antes de importar a API: o lifespan usa essa mesma engine.
    database = tmp_path_factory.mktemp("tasklab_testes") / "testes.db"
    with pytest.MonkeyPatch.context() as environment:
        environment.setenv("DATABASE_URL", f"sqlite:///{database.as_posix()}")
        environment.setenv("JWT_SECRET_KEY", secrets.token_hex(32))
        environment.setenv("JWT_ACCESS_TOKEN_EXPIRE_MINUTES", "60")

        from app.main import app
        from app.database import Base, engine

        # Evita que a limpeza alcance o banco principal.
        assert engine.url.database == database.as_posix()
        try:
            Base.metadata.drop_all(bind=engine)
            yield app
        finally:
            engine.dispose()


@pytest.fixture
def client(application):
    from app.database import Base, engine

    try:
        # O lifespan cria as tabelas no banco temporário.
        with TestClient(application) as test_client:
            yield test_client
    finally:
        # Cada teste começa sem dados deixados por outro caso.
        Base.metadata.drop_all(bind=engine)


SENHA = "SenhaInicial123!"


@pytest.fixture
def usuario_cadastrado(client, request):
    dados = {
        "name": "Aluno Teste",
        "email": f"{request.node.name.split('_')[1]}@example.com",
        "password": SENHA,
    }
    resposta = client.post("/auth/register", json=dados)
    assert resposta.status_code == 201
    return {**dados, "id": resposta.json()["id"]}


@pytest.fixture
def headers_autenticados(client, usuario_cadastrado):
    resposta = client.post(
        "/auth/login",
        json={
            "email": usuario_cadastrado["email"],
            "password": usuario_cadastrado["password"],
        },
    )
    assert resposta.status_code == 200
    token = resposta.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}
