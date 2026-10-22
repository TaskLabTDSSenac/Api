import secrets

import pytest
from fastapi.testclient import TestClient


@pytest.fixture(scope="session")
def application(tmp_path_factory):
    # Configura o ambiente ANTES de importar a aplicação e criar sua engine.
    database = tmp_path_factory.mktemp("tasklab") / "tests.db"
    with pytest.MonkeyPatch.context() as environment:
        environment.setenv("DATABASE_URL", f"sqlite:///{database.as_posix()}")
        environment.setenv("JWT_SECRET_KEY", secrets.token_hex(32))
        environment.setenv("JWT_ACCESS_TOKEN_EXPIRE_MINUTES", "60")
        from app.main import app
        from app.database import engine

        assert engine.url.database == database.as_posix()
        try:
            yield app
        finally:
            engine.dispose()


@pytest.fixture
def client(application):
    from app.database import Base, engine

    with TestClient(application) as client:
        yield client
    # Somente a engine temporária criada pela fixture application é utilizada.
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def users(client):
    result = []
    for name in ("ana", "bia"):
        credentials = {"email": f"{name}@example.com", "password": "SenhaSegura123"}
        response = client.post("/auth/register", json={"name": name, **credentials})
        assert response.status_code == 201
        login = client.post("/auth/login", json=credentials)
        assert login.status_code == 200
        result.append({"Authorization": f"Bearer {login.json()['access_token']}"})
    return result


@pytest.fixture
def task(client, users):
    response = client.post(
        "/tasks", headers=users[0],
        json={"title": "Tarefa original", "description": "Descrição original"},
    )
    assert response.status_code == 201
    return response.json()
