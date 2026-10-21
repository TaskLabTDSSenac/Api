from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.exception_handlers import request_validation_exception_handler
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.controllers.auth_controller import router as auth_router
from app.database import Base, engine
from app.exceptions import EmailAlreadyExistsError
from app.models.user import User  # Registra o modelo no metadata antes de create_all.


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(title="TaskLab API", version="0.1.0", lifespan=lifespan)
app.include_router(auth_router)


@app.exception_handler(EmailAlreadyExistsError)
async def email_already_exists_handler(request: Request, error: EmailAlreadyExistsError):
    return JSONResponse(status_code=409, content={"detail": "E-mail já cadastrado."})


@app.exception_handler(RequestValidationError)
async def validation_error_handler(request: Request, error: RequestValidationError):
    # Não ecoa valores recebidos: erros no corpo inteiro também podem conter a senha.
    errors = [{key: value for key, value in item.items() if key != "input"}
              for item in error.errors()]
    return await request_validation_exception_handler(request, RequestValidationError(errors))


@app.get("/health", tags=["Infraestrutura"])
def health() -> dict[str, str]:
    return {"status": "ok"}
