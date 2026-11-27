from types import SimpleNamespace
from unittest.mock import Mock

import pytest

from app.exceptions import IncorrectCurrentPasswordError, SamePasswordError
from app.schemas.user_schema import PasswordChangeRequest
from app.services.user_service import UserService


@pytest.fixture
def repository():
    return Mock()


@pytest.fixture
def service(repository):
    return UserService(repository)


def test_change_password_sucesso_atualiza_hash(service, repository, monkeypatch):
    import app.services.user_service as user_service_module

    user = SimpleNamespace(password_hash="hash-antigo")
    data = PasswordChangeRequest(current_password="senha-atual", new_password="senha-nova-segura")
    monkeypatch.setattr(user_service_module, "verify_password", lambda password, hashed: password == "senha-atual" and hashed == "hash-antigo")
    monkeypatch.setattr(user_service_module, "hash_password", lambda password: f"hash:{password}")

    result = service.change_password(user, data)

    assert result is None
    repository.update_password.assert_called_once_with(user, "hash:senha-nova-segura")


def test_change_password_senha_atual_incorreta(service, repository, monkeypatch):
    import app.services.user_service as user_service_module

    user = SimpleNamespace(password_hash="hash-cadastrado")
    data = PasswordChangeRequest(current_password="senha-errada", new_password="senha-nova-segura")
    monkeypatch.setattr(user_service_module, "verify_password", lambda password, hashed: False)

    with pytest.raises(IncorrectCurrentPasswordError):
        service.change_password(user, data)

    repository.update_password.assert_not_called()


def test_change_password_nova_igual_a_atual(service, repository, monkeypatch):
    import app.services.user_service as user_service_module

    user = SimpleNamespace(password_hash="hash-atual")
    data = PasswordChangeRequest(current_password="senha-atual", new_password="senha-atual")
    monkeypatch.setattr(user_service_module, "verify_password", lambda password, hashed: True)

    with pytest.raises(SamePasswordError):
        service.change_password(user, data)

    repository.update_password.assert_not_called()
