# TaskLab API

API didática para aulas de testes de software, desenvolvida com Python e FastAPI.
Nesta etapa inicial, disponibiliza um endpoint público para verificar se a API está respondendo.

## Preparação do ambiente no Windows

Utilize Python 3.12. Abra o PowerShell na pasta `Api`, que já é a raiz do repositório.
O ambiente virtual `.venv` já está preparado e deve ser reutilizado.

Para ativá-lo:

```powershell
.\.venv\Scripts\Activate.ps1
```

Os comandos abaixo usam diretamente o Python da `.venv`, portanto também funcionam sem ativação.

## Instalação das dependências

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

O arquivo `requirements.txt` fixa o FastAPI na versão 0.156.4, consultada no ambiente virtual existente.
O extra `standard` inclui o Uvicorn usado para executar a API.

## Execução com Uvicorn

Na raiz `Api`, execute:

```powershell
.\.venv\Scripts\python.exe -m uvicorn app.main:app --reload
```

A opção `--reload` reinicia o servidor ao alterar o código durante o desenvolvimento.
Para encerrar, pressione `Ctrl+C`.

## Endereços locais

- Saúde da API: <http://127.0.0.1:8000/health> — `GET` público, com HTTP 200 e resposta `{"status": "ok"}`.
- Documentação interativa (Swagger UI): <http://127.0.0.1:8000/docs>.
