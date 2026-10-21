# TaskLab API

API didática para aulas de testes de software, desenvolvida com Python e FastAPI.
Disponibiliza a verificação de saúde e o cadastro público de usuários com persistência em SQLite.
Login, JWT e tarefas ficam para etapas futuras.

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

## Execução

O comando principal, na raiz `Api`, é:

```powershell
.\iniciar.bat
```

Ele reutiliza a `.venv` (ou a cria se estiver ausente), instala o `requirements.txt`
e inicia o Uvicorn com recarga automática.

### Execução direta com Uvicorn

Na raiz `Api`, execute:

```powershell
.\.venv\Scripts\python.exe -m uvicorn app.main:app --reload
```

A opção `--reload` reinicia o servidor ao alterar o código durante o desenvolvimento.
Para encerrar, pressione `Ctrl+C`.

## Endereços locais

- Saúde da API: <http://127.0.0.1:8000/health> — `GET` público, com HTTP 200 e resposta `{"status": "ok"}`.
- Documentação interativa (Swagger UI): <http://127.0.0.1:8000/docs>.
- Cadastro: `POST http://127.0.0.1:8000/auth/register`.

## Configuração e banco de dados

Ao iniciar, a aplicação cria automaticamente `tasklab.db` na raiz do projeto e as
tabelas ausentes. O caminho padrão é calculado pela localização dos arquivos,
independentemente da pasta de execução. Bancos e tabelas existentes não são apagados.
`Base.metadata.create_all` cria tabelas ausentes, mas não substitui migrações para
alterações de esquema em tabelas existentes.

Para personalizar, copie `.env.example` para `.env` e defina `DATABASE_URL`, por exemplo:

```dotenv
DATABASE_URL=sqlite:///C:/dados/tasklab.db
```

A pasta escolhida deve existir. Variáveis de ambiente têm prioridade sobre `.env`.
Caminhos SQLite relativos personalizados são relativos à pasta de execução.
Cada requisição recebe uma sessão, fechada ao terminar. Cada conexão SQLite habilita
`PRAGMA foreign_keys=ON`. Os timestamps são gerados em UTC; o SQLite armazena os valores
sem informação de fuso, portanto devem ser interpretados como UTC.
`updated_at` é atualizado nas alterações feitas pelo SQLAlchemy.

`.venv`, `.env`, bancos `.db` e seus arquivos auxiliares são ignorados pelo Git.

## Fluxo do cadastro

`POST /auth/register` → Controller → Service → Repository → SQLite.

- `app/config.py`: lê as configurações com pydantic-settings.
- `app/database.py`: define engine, sessão, base dos modelos e configuração SQLite.
- `app/models/user.py`: mapeia a tabela `users`, com e-mail único e timestamps.
- `app/schemas/user_schema.py`: valida a entrada e limita a resposta a `id`, `name` e `email`.
- `app/controllers/auth_controller.py`: recebe o JSON, monta dependências e retorna HTTP 201.
- `app/services/auth_service.py`: verifica duplicidade, gera o hash e solicita a persistência.
- `app/repositories/user_repository.py`: consulta e salva; executa commit, refresh e rollback em falhas.
- `app/security/password.py`: gera hashes Argon2 com pwdlib, sem armazenar a senha original.
- `app/exceptions.py`: define a exceção de domínio para e-mail já cadastrado.
- `app/main.py`: registra rotas e handlers; cria as tabelas no lifespan.

O nome é aparado e deve ter de 1 a 150 caracteres. O e-mail é aparado, validado e
normalizado para minúsculas, com limite de 255 caracteres. A senha aceita de 8 a 128
caracteres, preservando espaços. Campos extras são rejeitados.
A restrição única do banco também protege contra cadastros concorrentes do mesmo e-mail.

## Verificações manuais no Swagger

Execute `iniciar.bat`, abra `/docs` e use **Try it out** em `POST /auth/register`:

```json
{
  "name": "  Ana Silva  ",
  "email": "  Ana.Silva@example.com  ",
  "password": "SenhaDidatica123!"
}
```

Em um banco sem esse e-mail, espere HTTP 201:

```json
{
  "id": 1,
  "name": "Ana Silva",
  "email": "ana.silva@example.com"
}
```

O ID pode variar conforme os cadastros existentes. Use apenas dados fictícios nas aulas.

| Cenário | Resultado esperado |
| --- | --- |
| Consultar `GET /health` | 200 com `{"status": "ok"}` |
| Cadastrar um novo e-mail válido | 201, sem senha ou hash na resposta |
| Repetir e-mail, inclusive mudando maiúsculas ou espaços externos | 409 com `{"detail": "E-mail já cadastrado."}` |
| Nome vazio, apenas espaços ou acima de 150 caracteres | 422 |
| E-mail inválido ou acima de 255 caracteres | 422 |
| Senha com menos de 8 ou mais de 128 caracteres | 422, sem ecoar a senha |
| Omitir um campo obrigatório ou enviar campo extra | 422 |
| Reiniciar a API e repetir um e-mail cadastrado | 409, confirmando persistência |

As respostas de validação preservam localização, tipo, mensagem e contexto do erro,
mas omitem os valores recebidos para evitar exposição de senhas.
