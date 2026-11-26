from unittest.mock import Mock

import pytest

from app.exceptions import IncorrectCurrentPasswordError, SamePasswordError
from app.models.user import User
from app.schemas.user_schema import PasswordChangeRequest
from app.services import user_service as user_service_module
from app.services.user_service import UserService


@pytest.fixture
def repository():
    return Mock()


@pytest.fixture
def service(repository):
    return UserService(repository)


@pytest.fixture
def user():
    return User(id=3, name="Pessoa", email="pessoa@example.com", password_hash="hash-antigo")


def test_change_password_updates_with_hash_of_new_password(service, repository, user, monkeypatch):
    verify = Mock(return_value=True)
    hash_new = Mock(return_value="hash-novo")
    monkeypatch.setattr(user_service_module, "verify_password", verify)
    monkeypatch.setattr(user_service_module, "hash_password", hash_new)
    data = PasswordChangeRequest(current_password="SenhaAtual1", new_password="SenhaNova2")

    result = service.change_password(user, data)

    assert result is None
    verify.assert_called_once_with("SenhaAtual1", "hash-antigo")
    hash_new.assert_called_once_with("SenhaNova2")
    repository.update_password.assert_called_once_with(user, "hash-novo")


def test_change_password_rejects_incorrect_current_password(service, repository, user, monkeypatch):
    verify = Mock(return_value=False)
    hash_new = Mock()
    monkeypatch.setattr(user_service_module, "verify_password", verify)
    monkeypatch.setattr(user_service_module, "hash_password", hash_new)
    data = PasswordChangeRequest(current_password="Errada123", new_password="SenhaNova2")

    with pytest.raises(IncorrectCurrentPasswordError):
        service.change_password(user, data)

    verify.assert_called_once_with("Errada123", "hash-antigo")
    hash_new.assert_not_called()
    repository.update_password.assert_not_called()


def test_change_password_rejects_same_password(service, repository, user, monkeypatch):
    verify = Mock(return_value=True)
    hash_new = Mock()
    monkeypatch.setattr(user_service_module, "verify_password", verify)
    monkeypatch.setattr(user_service_module, "hash_password", hash_new)
    data = PasswordChangeRequest(current_password="IgualSenha1", new_password="IgualSenha1")

    with pytest.raises(SamePasswordError):
        service.change_password(user, data)

    verify.assert_called_once_with("IgualSenha1", "hash-antigo")
    hash_new.assert_not_called()
    repository.update_password.assert_not_called()
