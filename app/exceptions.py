class EmailAlreadyExistsError(Exception):
    """O e-mail informado já pertence a um usuário."""


class InvalidCredentialsError(Exception):
    """E-mail ou senha inválidos."""


class AuthenticationRequiredError(Exception):
    """Autenticação necessária ou token inválido."""
