from unittest.mock import Mock, patch

import pytest


@pytest.fixture
def user_service_module(test_settings):
    from app.services import user_service

    return user_service


def test_change_password_updates_hash_after_current_password_verifies(user_service_module):
    repository = Mock(spec=user_service_module.UserRepository)
    user = Mock(spec=user_service_module.User)
    user.password_hash = "hash-atual"
    service = user_service_module.UserService(repository)
    data = user_service_module.PasswordChangeRequest(
        current_password="SenhaAtual123", new_password="SenhaNova123"
    )

    with patch.object(user_service_module, "verify_password", return_value=True) as verify:
        with patch.object(user_service_module, "hash_password", return_value="hash-novo") as hash_pw:
            result = service.change_password(user, data)

    assert result is None
    verify.assert_called_once_with(data.current_password, "hash-atual")
    hash_pw.assert_called_once_with(data.new_password)
    repository.update_password.assert_called_once_with(user, "hash-novo")


def test_change_password_rejects_incorrect_current_password(user_service_module):
    repository = Mock(spec=user_service_module.UserRepository)
    user = Mock(spec=user_service_module.User)
    user.password_hash = "hash-atual"
    service = user_service_module.UserService(repository)
    data = user_service_module.PasswordChangeRequest(
        current_password="Errada123", new_password="SenhaNova123"
    )

    with patch.object(user_service_module, "verify_password", return_value=False):
        with patch.object(user_service_module, "hash_password") as hash_pw:
            with pytest.raises(user_service_module.IncorrectCurrentPasswordError):
                service.change_password(user, data)

    hash_pw.assert_not_called()
    repository.update_password.assert_not_called()


def test_change_password_rejects_same_password(user_service_module):
    repository = Mock(spec=user_service_module.UserRepository)
    user = Mock(spec=user_service_module.User)
    user.password_hash = "hash-atual"
    service = user_service_module.UserService(repository)
    data = user_service_module.PasswordChangeRequest(
        current_password="MesmaSenha123", new_password="MesmaSenha123"
    )

    with patch.object(user_service_module, "verify_password", return_value=True):
        with patch.object(user_service_module, "hash_password") as hash_pw:
            with pytest.raises(user_service_module.SamePasswordError):
                service.change_password(user, data)

    hash_pw.assert_not_called()
    repository.update_password.assert_not_called()
