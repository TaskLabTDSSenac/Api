"""Inicia a API com um banco exclusivo, limpo a cada execução do BAT."""

import os
from pathlib import Path
import secrets
import socket
import sys


def main():
    root = Path(__file__).resolve().parent.parent
    database = root / "tasklab_web_testes.db"
    if database.is_symlink() or database.resolve() != database:
        raise RuntimeError("O banco de testes não pode apontar para outro arquivo.")

    # Não limpa os dados se outra API já estiver usando a porta.
    try:
        with socket.socket() as check:
            check.bind(("127.0.0.1", 8000))
    except OSError:
        raise RuntimeError(
            "A porta 8000 está ocupada. Encerre a outra API e execute novamente. "
            "O banco de testes não foi limpo."
        ) from None

    # Estas variáveis prevalecem sobre o .env, somente neste processo.
    os.environ["DATABASE_URL"] = f"sqlite:///{database.as_posix()}"
    os.environ["JWT_SECRET_KEY"] = secrets.token_hex(32)
    os.environ["JWT_ACCESS_TOKEN_EXPIRE_MINUTES"] = "60"
    sys.path.insert(0, str(root))

    import uvicorn
    from app.main import app
    from app.database import Base, engine

    assert Path(engine.url.database).resolve() == database
    try:
        # Remove e recria somente as tabelas do banco exclusivo dos testes Web.
        Base.metadata.drop_all(bind=engine)
        Base.metadata.create_all(bind=engine)
        print(f"Banco de testes limpo: {database}", flush=True)
        print("API: http://127.0.0.1:8000 | Para encerrar: Ctrl+C", flush=True)
        uvicorn.run(app, host="127.0.0.1", port=8000)
    finally:
        engine.dispose()


if __name__ == "__main__":
    main()
