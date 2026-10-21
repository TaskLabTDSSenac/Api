from datetime import datetime, timedelta, timezone

import jwt

from app.config import settings
from app.exceptions import AuthenticationRequiredError


ALGORITHM = "HS256"


def create_access_token(user_id: int) -> str:
    now = datetime.now(timezone.utc)
    payload = {
        "sub": str(user_id),
        "iat": now,
        "exp": now + timedelta(minutes=settings.jwt_access_token_expire_minutes),
    }
    return jwt.encode(payload, settings.jwt_secret_key.get_secret_value(), algorithm=ALGORITHM)


def decode_access_token(token: str) -> int:
    """Valida o token e devolve o ID autenticado, nunca dados enviados livremente."""
    try:
        payload = jwt.decode(
            token,
            settings.jwt_secret_key.get_secret_value(),
            algorithms=[ALGORITHM],
            options={"require": ["sub", "iat", "exp"]},
        )
        subject = payload["sub"]
        if not isinstance(subject, str) or not subject.isascii() or not subject.isdecimal():
            raise ValueError("Invalid subject")
        # IDs SQLite são inteiros positivos de até 64 bits.
        if len(subject) > 19 or not 0 < int(subject) <= 2**63 - 1:
            raise ValueError("Invalid user ID")
        if any(type(payload[claim]) is not int for claim in ("iat", "exp")):
            raise ValueError("Invalid timestamps")
        if payload["exp"] <= payload["iat"]:
            raise ValueError("Invalid expiration")
        return int(subject)
    except (jwt.InvalidTokenError, ValueError, TypeError, OverflowError):
        raise AuthenticationRequiredError() from None
