# TaskLab API

API didática para aulas de testes de software, desenvolvida com Python e FastAPI.
Disponibiliza a verificação de saúde e o cadastro público de usuários com persistência em SQLite.
Inclui login em JSON e identificação do usuário autenticado com JWT Bearer.
Tarefas, refresh token e logout no servidor ficam para etapas futuras.

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

## Preparação do segredo JWT

O `iniciar.bat` prepara a chave automaticamente. Para configurar manualmente antes
da execução direta pelo Uvicorn, copie `.env.example` para `.env` (se já existir,
edite-o sem sobrescrever suas configurações). Gere uma chave local:

```powershell
.\.venv\Scripts\python.exe -c "import secrets; print(secrets.token_hex(32))"
```

Copie a chave gerada para `.env`:

```dotenv
JWT_SECRET_KEY=CHAVE_GERADA
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=60
```

`CHAVE_GERADA` deve ser substituído pelo resultado do comando. O segredo é obrigatório,
deve ter pelo menos 32 bytes e deve permanecer estável entre reinícios. O placeholder
de `.env.example` é inválido. A aplicação recusa iniciar se a configuração for inválida,
sem exibir o segredo. Não publique `.env` ou a chave no repositório.
O prazo de expiração deve ser positivo; quando omitido, é de 60 minutos.

## Execução

O comando principal, na raiz `Api`, é:

```powershell
.\iniciar.bat
```

Ele reutiliza a `.venv` (ou a cria se estiver ausente), instala o `requirements.txt`,
gera e salva `JWT_SECRET_KEY` no `.env` se estiver ausente, vazia ou com o placeholder
do exemplo, e inicia o Uvicorn com recarga automática. Uma chave existente é preservada,
assim como as demais configurações do `.env`. Se o arquivo não existir, ele é criado.

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
- Login: `POST http://127.0.0.1:8000/auth/login`.
- Usuário autenticado: `GET http://127.0.0.1:8000/users/me`.

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

## Login e autenticação no Swagger

1. Configure `.env`, execute `.\iniciar.bat` e abra `/docs`.
2. Cadastre um usuário em `POST /auth/register`.
3. Execute `POST /auth/login` com o e-mail e a senha cadastrados, em JSON:

```json
{
  "email": "ana.silva@example.com",
  "password": "SenhaDidatica123!"
}
```

O sucesso retorna HTTP 200:

```json
{
  "access_token": "TOKEN_JWT",
  "token_type": "bearer"
}
```

4. Copie `access_token`, clique em **Authorize** e cole somente o token, sem `Bearer`.
5. Execute `GET /users/me`: a resposta contém somente `id`, `name` e `email`.

O Swagger usa HTTP Bearer. Em outros clientes, envie o cabeçalho
`Authorization: Bearer TOKEN_JWT`. O login continua recebendo JSON, sem formulário OAuth2.
O e-mail recebe a mesma normalização do cadastro. A senha não é modificada e aceita
de 1 a 128 caracteres no login; uma senha curta não vazia é verificada e resulta em
401 se incorreta. Entrada inválida ou campos extras resultam em 422, sem ecoar a senha.

| Cenário | Resultado esperado |
| --- | --- |
| Login com credenciais válidas | 200 com token Bearer |
| Senha incorreta ou e-mail não cadastrado | 401: `E-mail ou senha inválidos.` |
| `/users/me` com token válido | 200 com dados do usuário autenticado |
| Token ausente, adulterado, expirado, sem claims obrigatórios ou de usuário inexistente | 401: `Autenticação necessária ou token inválido.` |

Todas as respostas 401 incluem `WWW-Authenticate: Bearer`.

O fluxo de login é Controller → AuthService → UserRepository → SQLite. O service
verifica a senha com pwdlib e gera o JWT. Para e-mail inexistente, verifica um hash
fictício preparado uma vez por processo, reduzindo diferenças de tempo entre falhas.
`app/schemas/auth_schema.py` define a entrada e a resposta do login.
`app/security/jwt.py` emite e valida tokens com HS256 fixo, `sub` (ID), `iat` (emissão)
e `exp` (expiração), em UTC. `app/security/dependencies.py` valida o Bearer e consulta
o usuário pelo ID assinado; `app/controllers/user_controller.py` expõe `/users/me`.
Um `user_id` enviado livremente pelo cliente não determina a identidade autenticada.

A assinatura JWT **não criptografa seu conteúdo**: o payload pode ser lido e não deve
conter senhas ou outros segredos. O token expira após o prazo configurado (60 minutos
por padrão). Um futuro logout nos clientes descartará o token localmente, mas ele
continuará válido até expirar, pois ainda não existe revogação no servidor.
