from pathlib import Path

from pydantic import Field, SecretStr, ValidationError, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


PROJECT_ROOT = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    database_url: str = f"sqlite:///{(PROJECT_ROOT / 'tasklab.db').as_posix()}"
    jwt_secret_key: SecretStr
    jwt_access_token_expire_minutes: int = Field(default=60, gt=0)

    @field_validator("jwt_secret_key")
    @classmethod
    def validate_secret(cls, value: SecretStr) -> SecretStr:
        secret = value.get_secret_value()
        if len(secret.encode("utf-8")) < 32 or not secret.strip() or secret == "SUBSTITUA_PELA_CHAVE_GERADA_NAO_USE_ESTE_PLACEHOLDER":
            raise ValueError("JWT_SECRET_KEY deve conter uma chave gerada com pelo menos 32 bytes.")
        return value

    model_config = SettingsConfigDict(
        env_file=PROJECT_ROOT / ".env", env_file_encoding="utf-8", extra="ignore",
        hide_input_in_errors=True,
    )


try:
    settings = Settings()
except ValidationError as error:
    fields = ", ".join(str(item["loc"][0]).upper() for item in error.errors())
    raise RuntimeError(
        f"Configuração ausente ou inválida: {fields}. Confira o .env. "
        "JWT_SECRET_KEY é obrigatório e deve ter pelo menos 32 bytes; "
        "JWT_ACCESS_TOKEN_EXPIRE_MINUTES deve ser positivo."
    ) from None
