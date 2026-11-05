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

        # Impede executar a limpeza se a engine não for a de testes.
        assert engine.url.database == database.as_posix()
        try:
            # Limpa somente uma vez, antes do primeiro teste da sessão.
            Base.metadata.drop_all(bind=engine)
            yield app
        finally:
            engine.dispose()


@pytest.fixture
def client(application):
    # O contexto executa o lifespan, criando as tabelas no banco temporário.
    with TestClient(application) as test_client:
        yield test_client
    # Limpeza após cada teste desativada: os dados permanecem nesta sessão.
    # Base.metadata.drop_all(bind=engine)
