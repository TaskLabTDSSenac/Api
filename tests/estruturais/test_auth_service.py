"""Testes diretos do Service: preparar, executar e verificar."""

import sqlite3
from unittest.mock import Mock, patch

import pytest
from sqlalchemy.exc import IntegrityError

from app.exceptions import EmailAlreadyExistsError, InvalidCredentialsError
from app.schemas.auth_schema import LoginRequest
from app.schemas.user_schema import UserCreate


@pytest.fixture
def modulo_auth_service(test_settings):
    # O pytest entrega o retorno desta função aos testes que recebem "modulo_auth_service".
    # test_settings configura apenas variáveis de ambiente para os imports.
    # Não inicia a aplicação, não abre banco e não cria tabelas.
    from app.services import auth_service
    return auth_service


# Mock simula uma dependencia. return_value define o valor que ela devolve.
# modulo_auth_service.User é o modelo User importado pelo Service, após configurar o ambiente.
# spec=modulo_auth_service.User restringe a leitura aos atributos do modelo; não salva no banco.
# patch.object troca uma funcao apenas durante o bloco "with".
# pytest.raises verifica se o codigo levanta a excecao esperada.
# assert_called_once_with confere o histórico do mock: uma chamada com esses argumentos.
# Falha se não houve chamada, se houve mais de uma ou se os argumentos foram diferentes.
# Essa verificação não chama a função de novo e não busca nem salva registros.
# assert_not_called confere que o mock não recebeu nenhuma chamada.


def test_cadastro_com_email_disponivel(modulo_auth_service):
    # Cria um Repository falso. spec limita seus métodos aos do Repository real.
    repository = Mock(spec=modulo_auth_service.UserRepository)
    # None significa que a consulta não encontrou o e-mail.
    repository.get_by_email.return_value = None
    # Representa o usuário que seria criado, sem salvar nada no banco.
    usuario = Mock(spec=modulo_auth_service.User)
    usuario.id = 1
    # Quando o Service chamar create(), o Repository falso devolverá usuario.
    repository.create.return_value = usuario
    # Entrega o Repository falso ao Service que queremos testar.
    service = modulo_auth_service.AuthService(repository)
    # Monta os dados de entrada usando o schema real da aplicação.
    dados = UserCreate(name="Aluno Teste", email="aluno@example.com", password="Senha123")

    # Substitui o cálculo do hash por um resultado conhecido durante o teste.
    with patch.object(modulo_auth_service, "hash_password", return_value="hash-simulado") as gerar_hash:
        # Chama o método real de cadastro, sem fazer uma requisição HTTP.
        resultado = service.register(dados)

    # "is" confirma que o Service devolveu o mesmo objeto criado pelo Repository.
    assert resultado is usuario
    # Confere se register chamou get_by_email uma vez com dados.email.
    # Não faz outra consulta: aquela chamada já devolveu o None configurado acima.
    repository.get_by_email.assert_called_once_with(dados.email)
    # Confere se register chamou hash_password uma vez, passando dados.password.
    # Não calcula hash aqui: o mock já devolveu "hash-simulado" durante register.
    gerar_hash.assert_called_once_with(dados.password)
    # Confere se register chamou create uma vez com nome, e-mail e "hash-simulado".
    # Falha se passou a senha original no lugar do hash. Não salva nada aqui.
    repository.create.assert_called_once_with(dados.name, dados.email, "hash-simulado")


def test_cadastro_com_email_duplicado(modulo_auth_service):
    # Prepara um Repository falso que encontra um usuário com o mesmo e-mail.
    repository = Mock(spec=modulo_auth_service.UserRepository)
    usuario = Mock(spec=modulo_auth_service.User)
    usuario.id = 1
    repository.get_by_email.return_value = usuario
    service = modulo_auth_service.AuthService(repository)
    dados = UserCreate(name="Aluno Teste", email="aluno@example.com", password="Senha123")

    with patch.object(modulo_auth_service, "hash_password") as gerar_hash:
        # O teste falha se register não levantar o erro de e-mail duplicado.
        with pytest.raises(EmailAlreadyExistsError):
            service.register(dados)

    # Confere se register interrompeu o cadastro antes de chamar hash_password.
    gerar_hash.assert_not_called()
    # Confere se register também deixou de chamar create. Não impede uma chamada;
    # apenas faz o teste falhar se ela já tiver acontecido.
    repository.create.assert_not_called()


def test_cadastro_com_conflito_de_email_no_banco(modulo_auth_service):
    repository = Mock(spec=modulo_auth_service.UserRepository)
    repository.get_by_email.return_value = None
    erro_sqlite = sqlite3.IntegrityError("UNIQUE constraint failed: users.email")
    erro_sqlite.sqlite_errorcode = sqlite3.SQLITE_CONSTRAINT_UNIQUE
    erro_banco = IntegrityError("INSERT", {}, erro_sqlite)
    repository.create.side_effect = erro_banco
    service = modulo_auth_service.AuthService(repository)
    dados = UserCreate(name="Aluno Teste", email="aluno@example.com", password="Senha123")

    with patch.object(modulo_auth_service, "hash_password", return_value="hash-simulado"):
        with pytest.raises(EmailAlreadyExistsError) as erro:
            service.register(dados)

    assert erro.value.__cause__ is erro_banco
    repository.create.assert_called_once_with(dados.name, dados.email, "hash-simulado")


def test_cadastro_propaga_erro_de_integridade_nao_relacionado_a_email(modulo_auth_service):
    repository = Mock(spec=modulo_auth_service.UserRepository)
    repository.get_by_email.return_value = None
    erro_sqlite = sqlite3.IntegrityError("CHECK constraint failed: users.name")
    erro_sqlite.sqlite_errorcode = sqlite3.SQLITE_CONSTRAINT_CHECK
    erro_banco = IntegrityError("INSERT", {}, erro_sqlite)
    repository.create.side_effect = erro_banco
    service = modulo_auth_service.AuthService(repository)
    dados = UserCreate(name="Aluno Teste", email="aluno@example.com", password="Senha123")

    with patch.object(modulo_auth_service, "hash_password", return_value="hash-simulado"):
        with pytest.raises(IntegrityError) as erro:
            service.register(dados)

    assert erro.value is erro_banco
    repository.create.assert_called_once_with(dados.name, dados.email, "hash-simulado")


def test_login_com_usuario_inexistente(modulo_auth_service):
    # Prepara a consulta para não encontrar nenhum usuário.
    repository = Mock(spec=modulo_auth_service.UserRepository)
    repository.get_by_email.return_value = None
    service = modulo_auth_service.AuthService(repository)
    dados = LoginRequest(email="aluno@example.com", password="Senha123")

    # False simula uma verificação de senha que não passou.
    with patch.object(modulo_auth_service, "verify_password", return_value=False) as verificar_senha:
        # Substitui a emissão de JWT para verificar se ela foi chamada.
        with patch.object(modulo_auth_service, "create_access_token") as gerar_token:
            # Executa o login e exige o erro de credenciais inválidas.
            with pytest.raises(InvalidCredentialsError):
                service.login(dados)

    # Confere se login chamou get_by_email uma vez com o e-mail informado.
    repository.get_by_email.assert_called_once_with(dados.email)
    # Confere se login chamou verify_password uma vez com a senha e o hash fictício.
    # Não verifica a senha de novo: o mock já devolveu False durante login.
    verificar_senha.assert_called_once_with(dados.password, modulo_auth_service.DUMMY_PASSWORD_HASH)
    # Confere se login não chamou create_access_token para o usuário inexistente.
    gerar_token.assert_not_called()


def test_login_com_senha_incorreta(modulo_auth_service):
    # O usuário existe: o Repository devolve seu ID e seu hash armazenado.
    repository = Mock(spec=modulo_auth_service.UserRepository)
    usuario = Mock(spec=modulo_auth_service.User)
    usuario.id = 7
    usuario.password_hash = "hash-armazenado"
    repository.get_by_email.return_value = usuario
    service = modulo_auth_service.AuthService(repository)
    dados = LoginRequest(email="aluno@example.com", password="Senha123")

    # A senha não confere: simulamos False sem executar Argon2.
    with patch.object(modulo_auth_service, "verify_password", return_value=False) as verificar_senha:
        with patch.object(modulo_auth_service, "create_access_token") as gerar_token:
            with pytest.raises(InvalidCredentialsError):
                service.login(dados)

    # Confere se login chamou verify_password uma vez com a senha e o hash do usuário.
    # Não compara senhas aqui: apenas examina os argumentos registrados pelo mock.
    verificar_senha.assert_called_once_with(dados.password, "hash-armazenado")
    # Confere se nenhuma chamada para gerar token aconteceu após a senha incorreta.
    gerar_token.assert_not_called()


def test_login_com_credenciais_validas(modulo_auth_service):
    # Prepara um usuário existente e os dados que serão enviados ao login.
    repository = Mock(spec=modulo_auth_service.UserRepository)
    usuario = Mock(spec=modulo_auth_service.User)
    usuario.id = 7
    usuario.password_hash = "hash-armazenado"
    repository.get_by_email.return_value = usuario
    service = modulo_auth_service.AuthService(repository)
    dados = LoginRequest(email="aluno@example.com", password="Senha123")

    # True simula senha correta; o token também é simulado, sem JWT real.
    with patch.object(modulo_auth_service, "verify_password", return_value=True) as verificar_senha:
        with patch.object(modulo_auth_service, "create_access_token", return_value="token-simulado") as gerar_token:
            # Executa o método real, que deve aceitar as credenciais.
            resultado = service.login(dados)

    # Confere se login chamou verify_password uma vez com a senha e o hash do usuário.
    verificar_senha.assert_called_once_with(dados.password, "hash-armazenado")
    # Confere se login chamou create_access_token uma vez com o ID 7.
    # Não gera token aqui: o mock já devolveu "token-simulado" durante login.
    gerar_token.assert_called_once_with(7)
    # Confirma os dados devolvidos pelo Service ao finalizar o login.
    assert resultado.access_token == "token-simulado"
    assert resultado.token_type == "bearer"
