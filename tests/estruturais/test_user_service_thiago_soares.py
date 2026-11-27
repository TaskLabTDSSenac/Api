from unittest.mock import Mock, patch

import pytest

from app.exceptions import IncorrectCurrentPasswordError, SamePasswordError
from app.schemas.user_schema import PasswordChangeRequest

@pytest.fixture
def modulo_user_service(test_settings):
    from app.services import user_service
    return user_service

def test_senha_atual_incorreta(modulo_user_service):
    repository = Mock(spec=modulo_user_service.UserRepository)
    usuario = Mock(spec=modulo_user_service.User)
    usuario.id = 20
    usuario.password_hash = "hash-armazenado"
    service = modulo_user_service.UserService(repository)
    dados = PasswordChangeRequest(current_password="12345678", new_password="87654321")

    with patch.object(modulo_user_service, "verify_password", return_value=False) as verificar_senha:
        with pytest.raises(IncorrectCurrentPasswordError):
            service.change_password(usuario, dados)

    repository.update_password.assert_not_called()
    verificar_senha.assert_called_once_with(dados.current_password, "hash-armazenado")




def test_senha_atual_igual_a_senha_nova(modulo_user_service):
    repository = Mock(spec=modulo_user_service.UserRepository)
    usuario = Mock(spec=modulo_user_service.User)
    usuario.id = 21
    usuario.password_hash = "hash-armazenado"
    service = modulo_user_service.UserService(repository)
    dados = PasswordChangeRequest(current_password="12345678", new_password="12345678")

    with patch.object(modulo_user_service, "verify_password", return_value=True) as verificar_senha:
        with pytest.raises(SamePasswordError):
            service.change_password(usuario, dados)

    repository.update_password.assert_not_called()
    verificar_senha.assert_called_once_with(dados.current_password, "hash-armazenado")




def test_senha_atualizada_com_sucesso(modulo_user_service):
    repository = Mock(spec=modulo_user_service.UserRepository)
    usuario = Mock(spec=modulo_user_service.User)
    usuario.id = 21
    usuario.password_hash = "hash-armazenado"
    service = modulo_user_service.UserService(repository)
    dados = PasswordChangeRequest(current_password="12345678", new_password="87654321")
    
    with patch.object(modulo_user_service, "verify_password", return_value=True) as verificar_senha:
        with patch.object(modulo_user_service, "hash_password", return_value="hash-novo") as gerar_hash:
            service.change_password(usuario, dados)


    gerar_hash.assert_called_once_with(dados.new_password)
    repository.update_password.assert_called_once_with(usuario, "hash-novo")
    verificar_senha.assert_called_once_with(dados.current_password, "hash-armazenado")