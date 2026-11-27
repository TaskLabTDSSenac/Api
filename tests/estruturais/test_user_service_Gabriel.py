"""Testes diretos do UserService, com Repository e funções de senha simulados."""

import secrets
from unittest.mock import Mock, patch

import pytest

from app.exceptions import IncorrectCurrentPasswordError, SamePasswordError
from app.schemas.user_schema import PasswordChangeRequest


@pytest.fixture
def test_settings(monkeypatch, tmp_path):
    database = tmp_path / "testes.db"
    monkeypatch.setenv("DATABASE_URL", f"sqlite:///{database.as_posix()}")
    monkeypatch.setenv("JWT_SECRET_KEY", secrets.token_hex(32))
    monkeypatch.setenv("JWT_ACCESS_TOKEN_EXPIRE_MINUTES", "60")
    return database


@pytest.fixture
def modulo_user_service(test_settings):
    from app.services import user_service
    return user_service


def test_trocar_senha_com_sucesso(modulo_user_service):
    repository = Mock(spec=modulo_user_service.UserRepository)
    user = Mock(spec=modulo_user_service.User)
    user.password_hash = "hash-atual"
    service = modulo_user_service.UserService(repository)
    data = PasswordChangeRequest(current_password="SenhaAtual1", new_password="SenhaNova2")

    with patch.object(modulo_user_service, "verify_password", return_value=True) as verify:
        with patch.object(modulo_user_service, "hash_password", return_value="hash-novo") as hash_:
            result = service.change_password(user, data)

    assert result is None
    verify.assert_called_once_with("SenhaAtual1", "hash-atual")
    hash_.assert_called_once_with("SenhaNova2")
    repository.update_password.assert_called_once_with(user, "hash-novo")


def test_senha_atual_incorreta_nao_gera_hash_ou_atualiza(modulo_user_service):
    repository = Mock(spec=modulo_user_service.UserRepository)
    user = Mock(spec=modulo_user_service.User)
    user.password_hash = "hash-atual"
    service = modulo_user_service.UserService(repository)
    data = PasswordChangeRequest(current_password="Errada123", new_password="SenhaNova2")

    with patch.object(modulo_user_service, "verify_password", return_value=False) as verify:
        with patch.object(modulo_user_service, "hash_password") as hash_:
            with pytest.raises(IncorrectCurrentPasswordError) as error:
                service.change_password(user, data)

    assert str(error.value) == ""
    verify.assert_called_once_with("Errada123", "hash-atual")
    hash_.assert_not_called()
    repository.update_password.assert_not_called()


def test_mesma_senha_nao_gera_hash_ou_atualiza(modulo_user_service):
    repository = Mock(spec=modulo_user_service.UserRepository)
    user = Mock(spec=modulo_user_service.User)
    user.password_hash = "hash-atual"
    service = modulo_user_service.UserService(repository)
    data = PasswordChangeRequest(current_password="MesmaSenha1", new_password="MesmaSenha1")

    with patch.object(modulo_user_service, "verify_password", return_value=True) as verify:
        with patch.object(modulo_user_service, "hash_password") as hash_:
            with pytest.raises(SamePasswordError) as error:
                service.change_password(user, data)

    assert str(error.value) == ""
    verify.assert_called_once_with("MesmaSenha1", "hash-atual")
    hash_.assert_not_called()
    repository.update_password.assert_not_called()
