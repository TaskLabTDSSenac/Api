
from unittest.mock import Mock, patch

import pytest

from app.exceptions import IncorrectCurrentPasswordError
from app.schemas.user_schema import PasswordChangeRequest


@pytest.fixture
def modulo_user_service(test_settings):
    from app.services import user_service
    return user_service


def test_trocar_senha_com_senha_atual_incorreta(modulo_user_service):
    repository = Mock(spec=modulo_user_service.UserRepository)
    usuario = Mock(spec=modulo_user_service.User)
    usuario.password_hash = "hash-atual"
    service = modulo_user_service.UserService(repository)

    dados = PasswordChangeRequest(
        current_password="SenhaErrada123",
        new_password="SenhaNova456",
    )

    with patch.object(modulo_user_service, "verify_password", return_value=False):
        with pytest.raises(IncorrectCurrentPasswordError):
            service.change_password(usuario, dados)

    repository.update_password.assert_not_called()

