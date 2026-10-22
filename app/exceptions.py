class EmailAlreadyExistsError(Exception):
    """O e-mail informado já pertence a um usuário."""


class InvalidCredentialsError(Exception):
    """E-mail ou senha inválidos."""


class AuthenticationRequiredError(Exception):
    """Autenticação necessária ou token inválido."""


class TaskNotFoundError(Exception):
    """Tarefa não encontrada ou indisponível para o usuário autenticado."""


class TaskAlreadyCompletedError(Exception):
    """A tarefa já está concluída."""


class IncorrectCurrentPasswordError(Exception):
    """Senha atual incorreta."""


class SamePasswordError(Exception):
    """A nova senha deve ser diferente da senha atual."""
