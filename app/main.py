from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.exception_handlers import request_validation_exception_handler
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.controllers.auth_controller import router as auth_router
from app.controllers.user_controller import router as user_router
from app.controllers.task_controller import router as task_router
from app.database import Base, engine
from app.exceptions import AuthenticationRequiredError, EmailAlreadyExistsError, InvalidCredentialsError, TaskNotFoundError, TaskAlreadyCompletedError
from app.exceptions import IncorrectCurrentPasswordError, SamePasswordError
from app.models.user import User  # Registra o modelo no metadata antes de create_all.
from app.models.task import Task  # Registra a tabela de tarefas sem recriar as existentes.


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(title="TaskLab API", version="0.1.0", lifespan=lifespan)
app.include_router(auth_router)
app.include_router(user_router)
app.include_router(task_router)


@app.exception_handler(InvalidCredentialsError)
async def invalid_credentials_handler(request: Request, error: InvalidCredentialsError):
    return JSONResponse(
        status_code=401, content={"detail": "E-mail ou senha inválidos."},
        headers={"WWW-Authenticate": "Bearer"},
    )


@app.exception_handler(AuthenticationRequiredError)
async def authentication_required_handler(request: Request, error: AuthenticationRequiredError):
    return JSONResponse(
        status_code=401, content={"detail": "Autenticação necessária ou token inválido."},
        headers={"WWW-Authenticate": "Bearer"},
    )


@app.exception_handler(EmailAlreadyExistsError)
async def email_already_exists_handler(request: Request, error: EmailAlreadyExistsError):
    return JSONResponse(status_code=409, content={"detail": "E-mail já cadastrado."})


@app.exception_handler(RequestValidationError)
async def validation_error_handler(request: Request, error: RequestValidationError):
    # Omite todos os valores recebidos, inclusive password, current_password e
    # new_password dentro de objetos inválidos ou de erros no corpo inteiro.
    errors = [{key: value for key, value in item.items() if key != "input"}
              for item in error.errors()]
    return await request_validation_exception_handler(request, RequestValidationError(errors))


@app.exception_handler(TaskNotFoundError)
async def task_not_found_handler(request: Request, error: TaskNotFoundError):
    return JSONResponse(status_code=404, content={"detail": "Tarefa não encontrada."})


@app.get("/health", tags=["Infraestrutura"])
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.exception_handler(TaskAlreadyCompletedError)
async def task_already_completed_handler(request: Request, error: TaskAlreadyCompletedError):
    return JSONResponse(status_code=400, content={"detail": "A tarefa já está concluída."})


@app.exception_handler(IncorrectCurrentPasswordError)
async def incorrect_current_password_handler(request: Request, error: IncorrectCurrentPasswordError):
    return JSONResponse(status_code=400, content={"detail": "Senha atual incorreta."})


@app.exception_handler(SamePasswordError)
async def same_password_handler(request: Request, error: SamePasswordError):
    return JSONResponse(
        status_code=400,
        content={"detail": "A nova senha deve ser diferente da senha atual."},
    )
