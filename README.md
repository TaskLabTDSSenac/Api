# TaskLab API

API didática para aulas de testes de software, desenvolvida com Python e FastAPI.
Disponibiliza a verificação de saúde e o cadastro público de usuários com persistência em SQLite.
Inclui login em JSON e identificação do usuário autenticado com JWT Bearer.
Inclui criação, listagem, consulta, edição, conclusão e exclusão de tarefas por usuário.
Refresh token, reabertura de tarefas e logout no servidor ficam para etapas futuras.

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
- Troca de senha: `PATCH http://127.0.0.1:8000/users/me/password`.
- Tarefas: `POST` e `GET http://127.0.0.1:8000/tasks` (exigem autenticação).
- Consulta por ID: `GET http://127.0.0.1:8000/tasks/{id}` (exige autenticação).
- Edição: `PUT http://127.0.0.1:8000/tasks/{id}`.
- Conclusão: `PATCH http://127.0.0.1:8000/tasks/{id}/complete`.
- Exclusão: `DELETE http://127.0.0.1:8000/tasks/{id}`.

Todas as operações de tarefas exigem autenticação Bearer.

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

## Criação e listagem de tarefas

### Consulta de uma tarefa por ID

No Swagger (`/docs`), faça login e cole o token em **Authorize**. Crie uma tarefa
com `POST /tasks` ou use o ID de uma tarefa retornada por `GET /tasks`.
Abra `GET /tasks/{id}`, clique em **Try it out**, informe o ID e execute.

- Tarefa do usuário autenticado: HTTP 200 com o mesmo formato de `TaskResponse`
  mostrado abaixo (sem `user_id` e com timestamps em UTC).
- ID inexistente ou tarefa de outro usuário: HTTP 404 com
  `{"detail": "Tarefa não encontrada."}`.
- Token ausente ou inválido: HTTP 401.
- ID inválido (não inteiro, menor que 1 ou maior que o limite inteiro de 64 bits
  do SQLite): HTTP 422.

Para verificar o isolamento, autentique um segundo usuário e consulte o ID criado
pelo primeiro: o resultado deve ser o mesmo 404 de uma tarefa inexistente.
O controller encaminha a identidade autenticada ao service, que consulta o repository
e verifica a propriedade. O handler central converte a exceção de domínio em 404.

### Criar e listar

Após o login, use **Authorize** no Swagger para enviar o token Bearer.
Em `POST /tasks`, envie:

```json
{
  "title": "  Estudar testes de software  ",
  "description": "Revisar os cenários da aula."
}
```

A resposta é HTTP 201, com a tarefa pendente (`completed: false`):

```json
{
  "id": 1,
  "title": "Estudar testes de software",
  "description": "Revisar os cenários da aula.",
  "completed": false,
  "created_at": "2026-10-21T15:00:00Z",
  "updated_at": "2026-10-21T15:00:00Z"
}
```

IDs e datas são ilustrativos. Os timestamps são retornados em ISO 8601 com indicação
de UTC (`Z`). O título é obrigatório e deve ter de 3 a 150 caracteres após remover
espaços das extremidades. A descrição aceita até 500 caracteres; omitida ou enviada
como `null`, resulta em `null`. Não há remoção de espaços da descrição.
Campos extras são rejeitados com 422, incluindo `id`, `user_id`, `completed`,
`created_at` e `updated_at`.

`GET /tasks` retorna HTTP 200 com uma lista:

```json
[
  {
    "id": 1,
    "title": "Estudar testes de software",
    "description": "Revisar os cenários da aula.",
    "completed": false,
    "created_at": "2026-10-21T15:00:00Z",
    "updated_at": "2026-10-21T15:00:00Z"
  }
]
```

Sem tarefas, retorna `[]`. A consulta filtra no banco pelo usuário autenticado e
ordena por `created_at` decrescente, com desempate por `id` decrescente. O proprietário
vem exclusivamente do token validado; cada usuário vê apenas suas próprias tarefas.
As respostas não expõem `user_id`.

O fluxo é Controller → TaskService → TaskRepository → SQLite:

- `app/controllers/task_controller.py`: exige autenticação, recebe a entrada e usa `current_user.id`.
- `app/schemas/task_schema.py`: valida a entrada e formata a resposta com timestamps UTC.
- `app/services/task_service.py`: encaminha criação e listagem ao repository.
- `app/repositories/task_repository.py`: persiste com commit/refresh e rollback em falhas; filtra e ordena a consulta.
- `app/models/task.py`: define a tabela `tasks`, com chave estrangeira e índice em `user_id`.

O modelo é registrado antes de `create_all`: ao reiniciar, a tabela ausente é criada
sem apagar tabelas ou registros existentes.

### Verificações manuais de tarefas no Swagger

1. Autentique o usuário A e execute `GET /tasks`: em uma conta nova, espere `[]`.
2. Crie tarefas com e sem descrição. Espere 201, `completed: false` e descrição omitida como `null`.
3. Liste novamente: confira as tarefas mais recentes primeiro e os timestamps em UTC.
4. Reinicie a API e liste novamente para conferir a persistência.
5. Cadastre e autentique o usuário B, substituindo o token em **Authorize**: suas tarefas devem estar isoladas das de A.
6. Experimente os cenários abaixo em `POST /tasks`.

| Entrada | Resultado esperado |
| --- | --- |
| Título `ab` | 422 |
| Título `abc` ou `  abc  ` | 201, título salvo como `abc` |
| Título apenas com espaços | 422 |
| Título com 151 caracteres | 422 |
| Descrição com 501 caracteres | 422 |
| Envio de `user_id` ou `completed` | 422 |
| POST ou GET sem token, ou com token inválido | 401 com `WWW-Authenticate: Bearer` |

Para testar ausência de autenticação, remova o token em **Authorize**. A opção de
logout do Swagger apenas remove o token do cliente, sem revogá-lo no servidor.

## Editar, concluir e excluir tarefas

Faça login e use **Authorize** no Swagger. Crie uma tarefa e copie seu ID.

1. Em `PUT /tasks/{id}`, informe o ID e o JSON:

   ```json
   {
     "title": "Estudar testes automatizados",
     "description": "Implementar testes com pytest"
   }
   ```

   Espere HTTP 200 com a tarefa atualizada. O título é obrigatório, aparado e deve
   conter de 3 a 150 caracteres. A descrição aceita até 500 caracteres; omiti-la
   ou enviar `null` remove a descrição anterior. O PUT preserva ID, proprietário,
   `created_at` e `completed`, e atualiza `updated_at`, mesmo se o conteúdo for igual.
   Campos extras, incluindo `user_id`, `id` e `completed`, retornam 422.

2. Em `PATCH /tasks/{id}/complete`, informe o mesmo ID e execute sem corpo JSON.
   Espere HTTP 200 com `completed: true` e `updated_at` atualizado. Repita a chamada:
   espere HTTP 400 com `{"detail": "A tarefa já está concluída."}`. Não há reabertura.
   Uma tarefa concluída ainda pode ter título e descrição editados, sem mudar seu estado.

3. Em `DELETE /tasks/{id}`, informe o ID e execute. Espere HTTP 204 sem corpo.
   O registro é removido fisicamente. Consulte ou tente excluir o mesmo ID novamente:
   espere HTTP 404 com `{"detail": "Tarefa não encontrada."}`.

Nas três operações, tarefas inexistentes e tarefas de outro usuário retornam o mesmo
404. O repository consulta por ID e proprietário, e o service reutiliza `get_task`
para verificar o resultado antes de modificar ou excluir. A identificação do
proprietário vem somente do JWT. Sem autenticação válida, as rotas retornam 401.
Para verificar o isolamento, crie outra tarefa com A e tente modificá-la com o token
de B; confirme depois, com A, que os dados permanecem iguais.

## Testes automatizados

### Alteração de senha pelo Swagger

Faça login e informe o token em **Authorize**. Em
`PATCH /users/me/password`, envie:

```json
{
  "current_password": "SenhaAtual123",
  "new_password": "NovaSenha456"
}
```

Use a senha atual da conta autenticada. A API identifica a conta exclusivamente
pelo token; não envie ID, e-mail ou confirmação de senha.
`current_password` aceita de 1 a 128 caracteres e `new_password` de 8 a 128.
Espaços são preservados nas duas senhas. Campos extras são rejeitados com 422;
a confirmação da senha será responsabilidade das interfaces web e mobile.

O sucesso retorna HTTP 200:

```json
{"detail": "Senha alterada com sucesso."}
```

Somente `password_hash` (Argon2) e `updated_at` são atualizados. Dados pessoais,
tarefas e outras contas permanecem intactos. O controller encaminha o usuário
autenticado ao `UserService`, que verifica a senha atual e a diferença da nova
senha antes de chamar o `UserRepository`. Falhas de persistência executam rollback.
Nenhuma senha ou hash é retornado, e os valores recebidos são omitidos dos erros 422,
inclusive quando estiverem dentro de objetos inválidos. O corpo não é registrado em logs.

| Verificação manual | Resultado esperado |
| --- | --- |
| Sem token, token inválido ou expirado | 401 com `WWW-Authenticate: Bearer` |
| Senha atual incorreta | 400: `Senha atual incorreta.` |
| Nova senha igual à atual | 400: `A nova senha deve ser diferente da senha atual.` |
| Nova senha com 7 caracteres | 422 |
| Nova senha diferente com 8 caracteres e senha atual correta | 200 |
| Campo obrigatório ausente ou campo extra | 422 |
| Login com a senha antiga após a troca | 401 |
| Login com a nova senha | 200 |
| Consultar perfil e tarefas com o token anterior | 200, dados preservados |

Falhas de validação e de regra de negócio não alteram o hash nem `updated_at`.
A troca de senha **não invalida tokens já emitidos**: eles continuam válidos até
a expiração, conforme a política atual sem revogação. Apenas os novos logins
passam a exigir a nova senha. Não há recuperação de senha, refresh token ou revogação.

### Executar a suíte

As dependências de teste ficam separadas em `requirements-dev.txt`. Execute na raiz:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
.\.venv\Scripts\python.exe -m pytest -q
```

`pytest.ini` limita a descoberta à pasta `tests`. A fixture em `tests/conftest.py`
define um banco SQLite temporário e um segredo exclusivo antes de importar a
aplicação. Cada teste recebe tabelas limpas nesse banco; o banco da demonstração
e o `.env` local não são modificados.

`tests/test_tasks.py` verifica edição e validações, conclusão e repetição, exclusão
física e resposta vazia, persistência entre requisições, isolamento entre usuários,
autenticação, rotas existentes e os contratos publicados no Swagger.

`tests/test_password_change.py` verifica a troca de senha, erros de validação e
negócio sem mutações, sigilo dos valores em erros e logs capturados, preservação
de espaços, autenticação, rollback, logins com senha antiga/nova, manutenção de
tokens anteriores e preservação dos dados e de outras contas.
