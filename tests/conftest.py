import secrets

import pytest
from fastapi.testclient import TestClient


@pytest.fixture(scope="session")
def test_settings(tmp_path_factory):
    # Apenas configura variáveis: não abre banco nem cria tabelas.
    database = tmp_path_factory.mktemp("tasklab_testes") / "testes.db"
    with pytest.MonkeyPatch.context() as environment:
        environment.setenv("DATABASE_URL", f"sqlite:///{database.as_posix()}")
        environment.setenv("JWT_SECRET_KEY", secrets.token_hex(32))
        environment.setenv("JWT_ACCESS_TOKEN_EXPIRE_MINUTES", "60")
        yield database


@pytest.fixture(scope="session")
def application(test_settings):
    # Somente os testes funcionais precisam preparar a aplicação e o banco.
    from app.main import app
    from app.database import Base, engine

    # Impede executar a limpeza se a engine não for a de testes.
    assert engine.url.database == test_settings.as_posix()
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
