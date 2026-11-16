# TaskLab API

API didÃ¡tica para aulas de testes de software, desenvolvida com Python e FastAPI.
Disponibiliza a verificaÃ§Ã£o de saÃºde e o cadastro pÃºblico de usuÃ¡rios com persistÃªncia em SQLite.
Inclui login em JSON e identificaÃ§Ã£o do usuÃ¡rio autenticado com JWT Bearer.
Inclui criaÃ§Ã£o, listagem, consulta, ediÃ§Ã£o, conclusÃ£o e exclusÃ£o de tarefas por usuÃ¡rio.
Refresh token, reabertura de tarefas e logout no servidor ficam para etapas futuras.

## PreparaÃ§Ã£o do ambiente no Windows

Utilize Python 3.12. Abra o PowerShell na pasta `Api`, que jÃ¡ Ã© a raiz do repositÃ³rio.
O ambiente virtual `.venv` jÃ¡ estÃ¡ preparado e deve ser reutilizado.

Para ativÃ¡-lo:

```powershell
.\.venv\Scripts\Activate.ps1
```

Os comandos abaixo usam diretamente o Python da `.venv`, portanto tambÃ©m funcionam sem ativaÃ§Ã£o.

## InstalaÃ§Ã£o das dependÃªncias

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

O arquivo `requirements.txt` fixa o FastAPI na versÃ£o 0.156.4, consultada no ambiente virtual existente.
O extra `standard` inclui o Uvicorn usado para executar a API.

## PreparaÃ§Ã£o do segredo JWT

O `iniciar.bat` prepara a chave automaticamente. Para configurar manualmente antes
da execuÃ§Ã£o direta pelo Uvicorn, copie `.env.example` para `.env` (se jÃ¡ existir,
edite-o sem sobrescrever suas configuraÃ§Ãµes). Gere uma chave local:

```powershell
.\.venv\Scripts\python.exe -c "import secrets; print(secrets.token_hex(32))"
```

Copie a chave gerada para `.env`:

```dotenv
JWT_SECRET_KEY=CHAVE_GERADA
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=60
```

`CHAVE_GERADA` deve ser substituÃ­do pelo resultado do comando. O segredo Ã© obrigatÃ³rio,
deve ter pelo menos 32 bytes e deve permanecer estÃ¡vel entre reinÃ­cios. O placeholder
de `.env.example` Ã© invÃ¡lido. A aplicaÃ§Ã£o recusa iniciar se a configuraÃ§Ã£o for invÃ¡lida,
sem exibir o segredo. NÃ£o publique `.env` ou a chave no repositÃ³rio.
O prazo de expiraÃ§Ã£o deve ser positivo; quando omitido, Ã© de 60 minutos.

## ExecuÃ§Ã£o

O comando principal, na raiz `Api`, Ã©:

```powershell
.\iniciar.bat
```

Ele reutiliza a `.venv` (ou a cria se estiver ausente), instala o `requirements.txt`,
gera e salva `JWT_SECRET_KEY` no `.env` se estiver ausente, vazia ou com o placeholder
do exemplo, e inicia o Uvicorn com recarga automÃ¡tica. Uma chave existente Ã© preservada,
assim como as demais configuraÃ§Ãµes do `.env`. Se o arquivo nÃ£o existir, ele Ã© criado.

### ExecuÃ§Ã£o direta com Uvicorn

Na raiz `Api`, execute:

```powershell
.\.venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

A opÃ§Ã£o `--reload` reinicia o servidor ao alterar o cÃ³digo durante o desenvolvimento.
Para encerrar, pressione `Ctrl+C`.

## EndereÃ§os locais

### Acesso pelo emulador Android

O `iniciar.bat` escuta na porta 8000 na interface local (`--host 127.0.0.1`).
No computador, continue usando `http://127.0.0.1:8000`. No emulador padrÃ£o do
Android Studio, use `http://10.0.2.2:8000`, endereÃ§o jÃ¡ configurado no aplicativo
Flutter para Android. Esse endereÃ§o especial do emulador acessa a interface
local do computador, sem precisar expor a API Ã  rede local.

Execute o aplicativo em modo debug para usar HTTP local; o manifesto de debug
jÃ¡ permite esse trÃ¡fego. A versÃ£o release exige HTTPS. O aplicativo Android
nativo nÃ£o depende de CORS; a configuraÃ§Ã£o abaixo se aplica ao navegador.
Reinicie a API apÃ³s alterar o comando de inicializaÃ§Ã£o. Para conferir o acesso,
abra `http://10.0.2.2:8000/health` no navegador do emulador e confira
`{"status":"ok"}`. Essa configuraÃ§Ã£o atende ao computador e ao emulador padrÃ£o;
o acesso por um celular fÃ­sico na rede exige outra configuraÃ§Ã£o de escuta.

### CORS para o frontend local

A API permite explicitamente as origens `http://127.0.0.1:5500` e
`http://localhost:5500` para o Site, alÃ©m de `http://127.0.0.1:5501` e
`http://localhost:5501` para o aplicativo Flutter Web. Execute o Flutter Web
na porta 5501 (`flutter run -d chrome --web-port=5501`).
TambÃ©m estÃ£o autorizadas `http://localhost:63942` e `http://127.0.0.1:63942`
para a sessÃ£o local do aplicativo. O Flutter pode escolher uma porta diferente
a cada execuÃ§Ã£o sem `--web-port`; prefira fixar a porta 5501 para evitar novos
bloqueios de CORS. A origem inclui a porta: liberar 5501 nÃ£o libera outras portas.
SÃ£o permitidos os mÃ©todos GET, POST, PUT, PATCH, DELETE e OPTIONS
e os cabeÃ§alhos Authorization e Content-Type. O `CORSMiddleware` estÃ¡ registrado
uma Ãºnica vez em `app/main.py`, sem wildcard nas origens.

`allow_credentials=False`: o frontend envia JWT pelo cabeÃ§alho Authorization e
nÃ£o usa cookies de autenticaÃ§Ã£o. A configuraÃ§Ã£o Ã© fixa no cÃ³digo; nÃ£o hÃ¡ variÃ¡vel
CORS no `.env`. Reinicie a API apÃ³s esta alteraÃ§Ã£o.

Um preflight OPTIONS de uma origem permitida retorna 200 com
`Access-Control-Allow-Origin` correspondente. Uma origem nÃ£o permitida recebe
400 no preflight e nÃ£o recebe esse cabeÃ§alho. CORS controla o acesso pelo navegador;
as rotas protegidas continuam exigindo JWT, inclusive para origens permitidas.

### Rotas

- SaÃºde da API: <http://127.0.0.1:8000/health> â€” `GET` pÃºblico, com HTTP 200 e resposta `{"status": "ok"}`.
- DocumentaÃ§Ã£o interativa (Swagger UI): <http://127.0.0.1:8000/docs>.
- Cadastro: `POST http://127.0.0.1:8000/auth/register`.
- Login: `POST http://127.0.0.1:8000/auth/login`.
- UsuÃ¡rio autenticado: `GET http://127.0.0.1:8000/users/me`.
- Troca de senha: `PATCH http://127.0.0.1:8000/users/me/password`.
- Tarefas: `POST` e `GET http://127.0.0.1:8000/tasks` (exigem autenticaÃ§Ã£o).
- Consulta por ID: `GET http://127.0.0.1:8000/tasks/{id}` (exige autenticaÃ§Ã£o).
- EdiÃ§Ã£o: `PUT http://127.0.0.1:8000/tasks/{id}`.
- ConclusÃ£o: `PATCH http://127.0.0.1:8000/tasks/{id}/complete`.
- ExclusÃ£o: `DELETE http://127.0.0.1:8000/tasks/{id}`.

Todas as operaÃ§Ãµes de tarefas exigem autenticaÃ§Ã£o Bearer.

## ConfiguraÃ§Ã£o e banco de dados

Ao iniciar, a aplicaÃ§Ã£o cria automaticamente `tasklab.db` na raiz do projeto e as
tabelas ausentes. O caminho padrÃ£o Ã© calculado pela localizaÃ§Ã£o dos arquivos,
independentemente da pasta de execuÃ§Ã£o. Bancos e tabelas existentes nÃ£o sÃ£o apagados.
`Base.metadata.create_all` cria tabelas ausentes, mas nÃ£o substitui migraÃ§Ãµes para
alteraÃ§Ãµes de esquema em tabelas existentes.

Para personalizar, copie `.env.example` para `.env` e defina `DATABASE_URL`, por exemplo:

```dotenv
DATABASE_URL=sqlite:///C:/dados/tasklab.db
```

A pasta escolhida deve existir. VariÃ¡veis de ambiente tÃªm prioridade sobre `.env`.
Caminhos SQLite relativos personalizados sÃ£o relativos Ã  pasta de execuÃ§Ã£o.
Cada requisiÃ§Ã£o recebe uma sessÃ£o, fechada ao terminar. Cada conexÃ£o SQLite habilita
`PRAGMA foreign_keys=ON`. Os timestamps sÃ£o gerados em UTC; o SQLite armazena os valores
sem informaÃ§Ã£o de fuso, portanto devem ser interpretados como UTC.
`updated_at` Ã© atualizado nas alteraÃ§Ãµes feitas pelo SQLAlchemy.

`.venv`, `.env`, bancos `.db` e seus arquivos auxiliares sÃ£o ignorados pelo Git.

## Fluxo do cadastro

`POST /auth/register` â†’ Controller â†’ Service â†’ Repository â†’ SQLite.

- `app/config.py`: lÃª as configuraÃ§Ãµes com pydantic-settings.
- `app/database.py`: define engine, sessÃ£o, base dos modelos e configuraÃ§Ã£o SQLite.
- `app/models/user.py`: mapeia a tabela `users`, com e-mail Ãºnico e timestamps.
- `app/schemas/user_schema.py`: valida a entrada e limita a resposta a `id`, `name` e `email`.
- `app/controllers/auth_controller.py`: recebe o JSON, monta dependÃªncias e retorna HTTP 201.
- `app/services/auth_service.py`: verifica duplicidade, gera o hash e solicita a persistÃªncia.
- `app/repositories/user_repository.py`: consulta e salva; executa commit, refresh e rollback em falhas.
- `app/security/password.py`: gera hashes Argon2 com pwdlib, sem armazenar a senha original.
- `app/exceptions.py`: define a exceÃ§Ã£o de domÃ­nio para e-mail jÃ¡ cadastrado.
- `app/main.py`: registra rotas e handlers; cria as tabelas no lifespan.

O nome Ã© aparado e deve ter de 1 a 150 caracteres. O e-mail Ã© aparado, validado e
normalizado para minÃºsculas, com limite de 255 caracteres. A senha aceita de 8 a 128
caracteres, preservando espaÃ§os. Campos extras sÃ£o rejeitados.
A restriÃ§Ã£o Ãºnica do banco tambÃ©m protege contra cadastros concorrentes do mesmo e-mail.

## VerificaÃ§Ãµes manuais no Swagger

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

O ID pode variar conforme os cadastros existentes. Use apenas dados fictÃ­cios nas aulas.

| CenÃ¡rio | Resultado esperado |
| --- | --- |
| Consultar `GET /health` | 200 com `{"status": "ok"}` |
| Cadastrar um novo e-mail vÃ¡lido | 201, sem senha ou hash na resposta |
| Repetir e-mail, inclusive mudando maiÃºsculas ou espaÃ§os externos | 409 com `{"detail": "E-mail jÃ¡ cadastrado."}` |
| Nome vazio, apenas espaÃ§os ou acima de 150 caracteres | 422 |
| E-mail invÃ¡lido ou acima de 255 caracteres | 422 |
| Senha com menos de 8 ou mais de 128 caracteres | 422, sem ecoar a senha |
| Omitir um campo obrigatÃ³rio ou enviar campo extra | 422 |
| Reiniciar a API e repetir um e-mail cadastrado | 409, confirmando persistÃªncia |

As respostas de validaÃ§Ã£o preservam localizaÃ§Ã£o, tipo, mensagem e contexto do erro,
mas omitem os valores recebidos para evitar exposiÃ§Ã£o de senhas.

## Login e autenticaÃ§Ã£o no Swagger

1. Configure `.env`, execute `.\iniciar.bat` e abra `/docs`.
2. Cadastre um usuÃ¡rio em `POST /auth/register`.
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
5. Execute `GET /users/me`: a resposta contÃ©m somente `id`, `name` e `email`.

O Swagger usa HTTP Bearer. Em outros clientes, envie o cabeÃ§alho
`Authorization: Bearer TOKEN_JWT`. O login continua recebendo JSON, sem formulÃ¡rio OAuth2.
O e-mail recebe a mesma normalizaÃ§Ã£o do cadastro. A senha nÃ£o Ã© modificada e aceita
de 1 a 128 caracteres no login; uma senha curta nÃ£o vazia Ã© verificada e resulta em
401 se incorreta. Entrada invÃ¡lida ou campos extras resultam em 422, sem ecoar a senha.

| CenÃ¡rio | Resultado esperado |
| --- | --- |
| Login com credenciais vÃ¡lidas | 200 com token Bearer |
| Senha incorreta ou e-mail nÃ£o cadastrado | 401: `E-mail ou senha invÃ¡lidos.` |
| `/users/me` com token vÃ¡lido | 200 com dados do usuÃ¡rio autenticado |
| Token ausente, adulterado, expirado, sem claims obrigatÃ³rios ou de usuÃ¡rio inexistente | 401: `AutenticaÃ§Ã£o necessÃ¡ria ou token invÃ¡lido.` |

Todas as respostas 401 incluem `WWW-Authenticate: Bearer`.

O fluxo de login Ã© Controller â†’ AuthService â†’ UserRepository â†’ SQLite. O service
verifica a senha com pwdlib e gera o JWT. Para e-mail inexistente, verifica um hash
fictÃ­cio preparado uma vez por processo, reduzindo diferenÃ§as de tempo entre falhas.
`app/schemas/auth_schema.py` define a entrada e a resposta do login.
`app/security/jwt.py` emite e valida tokens com HS256 fixo, `sub` (ID), `iat` (emissÃ£o)
e `exp` (expiraÃ§Ã£o), em UTC. `app/security/dependencies.py` valida o Bearer e consulta
o usuÃ¡rio pelo ID assinado; `app/controllers/user_controller.py` expÃµe `/users/me`.
Um `user_id` enviado livremente pelo cliente nÃ£o determina a identidade autenticada.

A assinatura JWT **nÃ£o criptografa seu conteÃºdo**: o payload pode ser lido e nÃ£o deve
conter senhas ou outros segredos. O token expira apÃ³s o prazo configurado (60 minutos
por padrÃ£o). Um futuro logout nos clientes descartarÃ¡ o token localmente, mas ele
continuarÃ¡ vÃ¡lido atÃ© expirar, pois ainda nÃ£o existe revogaÃ§Ã£o no servidor.

## CriaÃ§Ã£o e listagem de tarefas

### Consulta de uma tarefa por ID

No Swagger (`/docs`), faÃ§a login e cole o token em **Authorize**. Crie uma tarefa
com `POST /tasks` ou use o ID de uma tarefa retornada por `GET /tasks`.
Abra `GET /tasks/{id}`, clique em **Try it out**, informe o ID e execute.

- Tarefa do usuÃ¡rio autenticado: HTTP 200 com o mesmo formato de `TaskResponse`
  mostrado abaixo (sem `user_id` e com timestamps em UTC).
- ID inexistente ou tarefa de outro usuÃ¡rio: HTTP 404 com
  `{"detail": "Tarefa nÃ£o encontrada."}`.
- Token ausente ou invÃ¡lido: HTTP 401.
- ID invÃ¡lido (nÃ£o inteiro, menor que 1 ou maior que o limite inteiro de 64 bits
  do SQLite): HTTP 422.

Para verificar o isolamento, autentique um segundo usuÃ¡rio e consulte o ID criado
pelo primeiro: o resultado deve ser o mesmo 404 de uma tarefa inexistente.
O controller encaminha a identidade autenticada ao service, que consulta o repository
e verifica a propriedade. O handler central converte a exceÃ§Ã£o de domÃ­nio em 404.

### Criar e listar

ApÃ³s o login, use **Authorize** no Swagger para enviar o token Bearer.
Em `POST /tasks`, envie:

```json
{
  "title": "  Estudar testes de software  ",
  "description": "Revisar os cenÃ¡rios da aula."
}
```

A resposta Ã© HTTP 201, com a tarefa pendente (`completed: false`):

```json
{
  "id": 1,
  "title": "Estudar testes de software",
  "description": "Revisar os cenÃ¡rios da aula.",
  "completed": false,
  "created_at": "2026-10-21T15:00:00Z",
  "updated_at": "2026-10-21T15:00:00Z"
}
```

IDs e datas sÃ£o ilustrativos. Os timestamps sÃ£o retornados em ISO 8601 com indicaÃ§Ã£o
de UTC (`Z`). O tÃ­tulo Ã© obrigatÃ³rio e deve ter de 3 a 150 caracteres apÃ³s remover
espaÃ§os das extremidades. A descriÃ§Ã£o aceita atÃ© 500 caracteres; omitida ou enviada
como `null`, resulta em `null`. NÃ£o hÃ¡ remoÃ§Ã£o de espaÃ§os da descriÃ§Ã£o.
Campos extras sÃ£o rejeitados com 422, incluindo `id`, `user_id`, `completed`,
`created_at` e `updated_at`.

`GET /tasks` retorna HTTP 200 com uma lista. Exige JWT e aceita os filtros
opcionais `completed` e `search`, que podem ser combinados:

| URL | Resultado |
| --- | --- |
| `/tasks` | Todas as tarefas do usuÃ¡rio autenticado. |
| `/tasks?completed=false` | Somente pendentes. |
| `/tasks?completed=true` | Somente concluÃ­das. |
| `/tasks?search=estudar` | TÃ­tulo ou descriÃ§Ã£o contendo â€œestudarâ€. |
| `/tasks?completed=false&search=estudar` | Pendentes com o texto no tÃ­tulo ou descriÃ§Ã£o. |
| `/tasks?search=100%25` | Busca o texto literal `100%`. |
| `/tasks?search=etapa_1` | Busca o texto literal `etapa_1`. |

Use o prefixo `http://127.0.0.1:8000` para acessar essas URLs localmente.
A busca ignora diferenÃ§as de maiÃºsculas/minÃºsculas, inclusive em palavras
acentuadas no SQLite, e remove espaÃ§os das extremidades. `search` vazio ou
composto sÃ³ por espaÃ§os nÃ£o restringe a consulta. DescriÃ§Ãµes nulas sÃ£o aceitas.
Os caracteres `%` e `_` nÃ£o sÃ£o curingas. O filtro Ã© aplicado no banco com
parÃ¢metros vinculados pelo SQLAlchemy, preservando a ordenaÃ§Ã£o por `created_at`
decrescente e, em empate, `id` decrescente. Sem resultados, retorna `[]`.

`completed` usa a validaÃ§Ã£o booleana do FastAPI; um valor nÃ£o reconhecido,
como `/tasks?completed=invalido`, retorna HTTP 422. O proprietÃ¡rio sempre Ã©
obtido do JWT; um parÃ¢metro `user_id` nÃ£o seleciona outra conta.

Exemplo do formato da lista, preservado sem paginaÃ§Ã£o:

```json
[
  {
    "id": 1,
    "title": "Estudar testes de software",
    "description": "Revisar os cenÃ¡rios da aula.",
    "completed": false,
    "created_at": "2026-10-21T15:00:00Z",
    "updated_at": "2026-10-21T15:00:00Z"
  }
]
```

Sem tarefas, retorna `[]`. A consulta filtra no banco pelo usuÃ¡rio autenticado e
ordena por `created_at` decrescente, com desempate por `id` decrescente. O proprietÃ¡rio
vem exclusivamente do token validado; cada usuÃ¡rio vÃª apenas suas prÃ³prias tarefas.
As respostas nÃ£o expÃµem `user_id`.

O fluxo Ã© Controller â†’ TaskService â†’ TaskRepository â†’ SQLite:

- `app/controllers/task_controller.py`: exige autenticaÃ§Ã£o, recebe a entrada e usa `current_user.id`.
- `app/schemas/task_schema.py`: valida a entrada e formata a resposta com timestamps UTC.
- `app/services/task_service.py`: encaminha criaÃ§Ã£o e listagem ao repository.
- `app/repositories/task_repository.py`: persiste com commit/refresh e rollback em falhas; filtra e ordena a consulta.
- `app/models/task.py`: define a tabela `tasks`, com chave estrangeira e Ã­ndice em `user_id`.

O modelo Ã© registrado antes de `create_all`: ao reiniciar, a tabela ausente Ã© criada
sem apagar tabelas ou registros existentes.

### EstatÃ­sticas das tarefas

`GET http://127.0.0.1:8000/tasks/stats` exige JWT e retorna todas as contagens
do usuÃ¡rio autenticado, independentemente dos filtros usados na listagem:

```json
{
  "total": 10,
  "pending": 6,
  "completed": 4,
  "completion_percentage": 40.0
}
```

As contagens sÃ£o calculadas no banco por agregaÃ§Ãµes, sem carregar as tarefas
em memÃ³ria. O service calcula `(completed / total) * 100`, arredondado para
duas casas decimais. Sem tarefas, retorna `total`, `pending` e `completed`
iguais a `0`, e `completion_percentage` igual a `0.0`.
O percentual Ã© um nÃºmero JSON; nÃ£o exige exibiÃ§Ã£o de zeros decimais Ã  direita.

O schema `TaskStatsResponse` e os parÃ¢metros da listagem aparecem no Swagger.
A rota `/tasks/stats` Ã© declarada antes de `/tasks/{id}`. Tanto a listagem
quanto as estatÃ­sticas reutilizam `get_current_user` e preservam o HTTP 401
para token ausente, invÃ¡lido ou expirado.

### VerificaÃ§Ãµes manuais de tarefas no Swagger

1. Autentique o usuÃ¡rio A e execute `GET /tasks`: em uma conta nova, espere `[]`.
2. Crie tarefas com e sem descriÃ§Ã£o. Espere 201, `completed: false` e descriÃ§Ã£o omitida como `null`.
3. Liste novamente: confira as tarefas mais recentes primeiro e os timestamps em UTC.
4. Reinicie a API e liste novamente para conferir a persistÃªncia.
5. Cadastre e autentique o usuÃ¡rio B, substituindo o token em **Authorize**: suas tarefas devem estar isoladas das de A.
6. Experimente os cenÃ¡rios abaixo em `POST /tasks`.

| Entrada | Resultado esperado |
| --- | --- |
| TÃ­tulo `ab` | 422 |
| TÃ­tulo `abc` ou `  abc  ` | 201, tÃ­tulo salvo como `abc` |
| TÃ­tulo apenas com espaÃ§os | 422 |
| TÃ­tulo com 151 caracteres | 422 |
| DescriÃ§Ã£o com 501 caracteres | 422 |
| Envio de `user_id` ou `completed` | 422 |
| POST ou GET sem token, ou com token invÃ¡lido | 401 com `WWW-Authenticate: Bearer` |

Para testar ausÃªncia de autenticaÃ§Ã£o, remova o token em **Authorize**. A opÃ§Ã£o de
logout do Swagger apenas remove o token do cliente, sem revogÃ¡-lo no servidor.

## Editar, concluir e excluir tarefas

FaÃ§a login e use **Authorize** no Swagger. Crie uma tarefa e copie seu ID.

1. Em `PUT /tasks/{id}`, informe o ID e o JSON:

   ```json
   {
     "title": "Estudar testes automatizados",
     "description": "Implementar testes com pytest"
   }
   ```

   Espere HTTP 200 com a tarefa atualizada. O tÃ­tulo Ã© obrigatÃ³rio, aparado e deve
   conter de 3 a 150 caracteres. A descriÃ§Ã£o aceita atÃ© 500 caracteres; omiti-la
   ou enviar `null` remove a descriÃ§Ã£o anterior. O PUT preserva ID, proprietÃ¡rio,
   `created_at` e `completed`, e atualiza `updated_at`, mesmo se o conteÃºdo for igual.
   Campos extras, incluindo `user_id`, `id` e `completed`, retornam 422.

2. Em `PATCH /tasks/{id}/complete`, informe o mesmo ID e execute sem corpo JSON.
   Espere HTTP 200 com `completed: true` e `updated_at` atualizado. Repita a chamada:
   espere HTTP 400 com `{"detail": "A tarefa jÃ¡ estÃ¡ concluÃ­da."}`. NÃ£o hÃ¡ reabertura.
   Uma tarefa concluÃ­da ainda pode ter tÃ­tulo e descriÃ§Ã£o editados, sem mudar seu estado.

3. Em `DELETE /tasks/{id}`, informe o ID e execute. Espere HTTP 204 sem corpo.
   O registro Ã© removido fisicamente. Consulte ou tente excluir o mesmo ID novamente:
   espere HTTP 404 com `{"detail": "Tarefa nÃ£o encontrada."}`.

Nas trÃªs operaÃ§Ãµes, tarefas inexistentes e tarefas de outro usuÃ¡rio retornam o mesmo
404. O repository consulta por ID e proprietÃ¡rio, e o service reutiliza `get_task`
para verificar o resultado antes de modificar ou excluir. A identificaÃ§Ã£o do
proprietÃ¡rio vem somente do JWT. Sem autenticaÃ§Ã£o vÃ¡lida, as rotas retornam 401.
Para verificar o isolamento, crie outra tarefa com A e tente modificÃ¡-la com o token
de B; confirme depois, com A, que os dados permanecem iguais.

## Testes automatizados

### AlteraÃ§Ã£o de senha pelo Swagger

FaÃ§a login e informe o token em **Authorize**. Em
`PATCH /users/me/password`, envie:

```json
{
  "current_password": "SenhaAtual123",
  "new_password": "NovaSenha456"
}
```

Use a senha atual da conta autenticada. A API identifica a conta exclusivamente
pelo token; nÃ£o envie ID, e-mail ou confirmaÃ§Ã£o de senha.
`current_password` aceita de 1 a 128 caracteres e `new_password` de 8 a 128.
EspaÃ§os sÃ£o preservados nas duas senhas. Campos extras sÃ£o rejeitados com 422;
a confirmaÃ§Ã£o da senha serÃ¡ responsabilidade das interfaces web e mobile.

O sucesso retorna HTTP 200:

```json
{"detail": "Senha alterada com sucesso."}
```

Somente `password_hash` (Argon2) e `updated_at` sÃ£o atualizados. Dados pessoais,
tarefas e outras contas permanecem intactos. O controller encaminha o usuÃ¡rio
autenticado ao `UserService`, que verifica a senha atual e a diferenÃ§a da nova
senha antes de chamar o `UserRepository`. Falhas de persistÃªncia executam rollback.
Nenhuma senha ou hash Ã© retornado, e os valores recebidos sÃ£o omitidos dos erros 422,
inclusive quando estiverem dentro de objetos invÃ¡lidos. O corpo nÃ£o Ã© registrado em logs.

| VerificaÃ§Ã£o manual | Resultado esperado |
| --- | --- |
| Sem token, token invÃ¡lido ou expirado | 401 com `WWW-Authenticate: Bearer` |
| Senha atual incorreta | 400: `Senha atual incorreta.` |
| Nova senha igual Ã  atual | 400: `A nova senha deve ser diferente da senha atual.` |
| Nova senha com 7 caracteres | 422 |
| Nova senha diferente com 8 caracteres e senha atual correta | 200 |
| Campo obrigatÃ³rio ausente ou campo extra | 422 |
| Login com a senha antiga apÃ³s a troca | 401 |
| Login com a nova senha | 200 |
| Consultar perfil e tarefas com o token anterior | 200, dados preservados |

Falhas de validaÃ§Ã£o e de regra de negÃ³cio nÃ£o alteram o hash nem `updated_at`.
A troca de senha **nÃ£o invalida tokens jÃ¡ emitidos**: eles continuam vÃ¡lidos atÃ©
a expiraÃ§Ã£o, conforme a polÃ­tica atual sem revogaÃ§Ã£o. Apenas os novos logins
passam a exigir a nova senha. NÃ£o hÃ¡ recuperaÃ§Ã£o de senha, refresh token ou revogaÃ§Ã£o.

### API com banco exclusivo para testes do Site

Na pasta `Api`, execute:

```powershell
.\iniciar_testes_site_app.bat
```

Esse arquivo inicia a API na porta 8000 e, a cada execuÃ§Ã£o, remove e recria
as tabelas de `Api/tasklab_web_testes.db`. O arquivo Ã© criado se ainda nÃ£o existir.
Todos os usuÃ¡rios e tarefas desse banco de testes sÃ£o apagados no inÃ­cio.
O banco principal `tasklab.db` e o `.env` sÃ£o preservados. A chave JWT Ã© gerada
apenas para essa execuÃ§Ã£o, portanto faÃ§a login novamente ao reiniciar.

Encerre a API anterior antes de executar: se a porta 8000 estiver ocupada,
o script interrompe antes da limpeza. A `.venv` e as dependÃªncias da API devem
estar instaladas. O auxiliar `scripts/iniciar_api_testes_site.py` fixa o caminho
do banco de testes antes de importar a aplicaÃ§Ã£o e executa a limpeza.

Mantenha essa janela aberta. Em outras janelas, execute `Site/iniciar.bat`
para servir as pÃ¡ginas e `Site/iniciar_testes.bat` para rodar o Playwright.
O BAT da API prepara o backend; ele nÃ£o inicia o site nem executa o Playwright.
Encerre com Ctrl+C. O banco permanece disponÃ­vel atÃ© a prÃ³xima execuÃ§Ã£o desse BAT.

### Testes da API com pytest

Na raiz `Api`, execute `iniciar_testes.bat` (tambÃ©m pode abrir com duplo clique).
Ele reutiliza a `.venv`, instala as dependÃªncias de desenvolvimento e executa
os testes, mantendo a janela aberta para leitura do resultado.

Para instalar e executar manualmente:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
.\.venv\Scripts\python.exe -m pytest -v
```

NÃ£o Ã© necessÃ¡rio iniciar o Uvicorn. O `FastAPI TestClient` chama a aplicaÃ§Ã£o
diretamente. `pytest.ini` organiza a descoberta na pasta `tests` e permite
importar o pacote `app`.

A fixture `client` em `tests/conftest.py` fornece um cliente reutilizÃ¡vel e
configura um SQLite temporÃ¡rio exclusivo antes de importar a API. O lifespan
cria as tabelas nesse banco. A limpeza ocorre uma Ãºnica vez antes do primeiro
teste; os dados permanecem disponÃ­veis para os prÃ³ximos testes da sessÃ£o. O banco
`tasklab.db` e o `.env` nÃ£o sÃ£o alterados; a chave JWT dos testes Ã© temporÃ¡ria.
Novos testes devem usar essa fixture e evitar importar a aplicaÃ§Ã£o no topo
dos arquivos, antes de configurar o ambiente isolado.

Os defeitos didÃ¡ticos foram corrigidos em 13/11/2026. Cadastro exige nome de
3 a 150 caracteres apÃ³s trim e senha de 8 a 128 caracteres. TÃ­tulos exigem
3 a 150 caracteres apÃ³s trim tanto na criaÃ§Ã£o quanto na ediÃ§Ã£o. A ediÃ§Ã£o
persiste a descriÃ§Ã£o, a segunda conclusÃ£o retorna 400 e a exclusÃ£o remove
a tarefa. Os clientes voltaram a comparar a confirmaÃ§Ã£o das senhas.
Registros antigos nÃ£o foram alterados ou apagados automaticamente.

Com o defeito intencional atual, a API retorna **201** e o teste aparece como
**FAILED** (`assert 201 == 422`). Isso demonstra a detecÃ§Ã£o do defeito; a regra
de negÃ³cio nÃ£o foi corrigida nem o teste marcado para ignorar a falha.

### Testes de carga com Locust

O arquivo `load_tests/locustfile.py` simula usuÃ¡rios autenticados consultando o perfil,
listando tarefas e consultando estatÃ­sticas. Configure `TASKLAB_TOKEN` com o token
Bearer de uma conta existente e mantenha a API iniciada em `http://127.0.0.1:8000`.

No PowerShell, na raiz `Api`:

```powershell
$env:TASKLAB_TOKEN = "SEU_ACCESS_TOKEN"
.\iniciar_teste_carga.bat
```

O Locust abre a interface em `http://localhost:8089`. Informe a quantidade de usuÃ¡rios
e a taxa de inicializaÃ§Ã£o, depois inicie o teste e ajuste a duraÃ§Ã£o na interface ou
passe opÃ§Ãµes diretamente ao BAT, por exemplo `--headless -u 10 -r 2 -t 1m`.
Os pesos das tarefas definem a proporÃ§Ã£o aproximada das chamadas: listagem 5,
perfil 3 e estatÃ­sticas 2. As tags `perfil`, `tarefas` e `estatisticas` permitem
selecionar rotas especÃ­ficas com `--tags` ou `--exclude-tags`.

A tabela do Locust mostra requisiÃ§Ãµes por segundo, tempos de resposta (incluindo
mediana e percentis), quantidade de requisiÃ§Ãµes e falhas. O relatÃ³rio pode ser salvo
com as opÃ§Ãµes `--csv` e `--html` do Locust.
O arquivo `tests/test_cadastro.py` atualmente verifica cadastro vÃ¡lido e login.
Embora o nome do primeiro teste mencione senha curta, seu corpo usa 8 caracteres
e espera 201. Ele foi preservado; nÃ£o comprova a rejeiÃ§Ã£o de senhas curtas.

## Testes estruturais do AuthService

NÃ£o Ã© necessÃ¡rio iniciar API, Site ou App. Na raiz da API, execute:

```powershell
.\iniciar_testes_estruturais.bat
```

O script usa o Python da `.venv`, instala `requirements-dev.txt` e executa
somente `tests/estruturais/`. Mostra cobertura de linhas e desvios no terminal,
incluindo eventuais linhas nÃ£o cobertas, e preserva o cÃ³digo de saÃ­da do pytest.
Abra `htmlcov_estruturais/index.html` no navegador para consultar o relatÃ³rio.

Para executar diretamente, sem a pausa do BAT:

```powershell
.\.venv\Scripts\python.exe -m pytest tests/estruturais/ -v --cov=app.services.auth_service --cov-branch --cov-report=term-missing --cov-report=html:htmlcov_estruturais
```

Esse comando mede exclusivamente `app/services/auth_service.py`.
`pytest-cov` estÃ¡ declarado em `requirements-dev.txt`; instale esse arquivo
antes da execuÃ§Ã£o direta caso ainda nÃ£o tenha as dependÃªncias.

`tests/estruturais/test_auth_service.py` chama `register` e `login` diretamente,
sem HTTP. Os mocks substituem Repository, geraÃ§Ã£o e verificaÃ§Ã£o de hash e
emissÃ£o de JWT, permitindo controlar as respostas e verificar chamadas.
A fixture `application` de `tests/conftest.py` Ã© reutilizada para configurar
o SQLite temporÃ¡rio antes dos imports: seu preparo pode acessar esse banco
isolado, mas as operaÃ§Ãµes dos Services usam apenas o Repository simulado.
NÃ£o utiliza o banco principal nem a fixture HTTP `client`. O hash fictÃ­cio
do mÃ³dulo Ã© criado normalmente no import; sua verificaÃ§Ã£o nos testes Ã© simulada.

Os nove casos verificam:

- E-mail disponÃ­vel: gera hash e salva os dados com esse hash.
- E-mail ocupado: lanÃ§a erro e nÃ£o gera hash nem salva.
- UsuÃ¡rio inexistente: verifica o hash fictÃ­cio e nÃ£o emite token.
- Senha incorreta: rejeita o login sem emitir token.
- Login vÃ¡lido: emite token para o ID correto e retorna tipo `bearer`.
- Duplicidade durante a persistÃªncia: converte a restriÃ§Ã£o de `users.email`
  em `EmailAlreadyExistsError`, preservando a causa.
- Outros erros de integridade: propaga o erro original para origem nÃ£o SQLite,
  outro cÃ³digo SQLite ou outra coluna com restriÃ§Ã£o Ãºnica (trÃªs casos).

Na verificaÃ§Ã£o de implementaÃ§Ã£o, os nove casos passaram com 100% das 32
instruÃ§Ãµes e dos 6 desvios medidos, sem linhas ou desvios pendentes.
Isso nÃ£o significa testar todas as combinaÃ§Ãµes: cobertura de branches observa
as alternativas do fluxo, mas nÃ£o garante todas as combinaÃ§Ãµes de condiÃ§Ãµes
de um `and`/`or`, todos os dados de entrada ou todas as sequÃªncias de execuÃ§Ã£o.
Estes testes tambÃ©m nÃ£o validam Argon2, JWT real ou concorrÃªncia real no banco:
essas dependÃªncias sÃ£o simuladas para verificar as decisÃµes do Service.
NÃ£o foram adicionadas exclusÃµes de cobertura nem alteradas regras de negÃ³cio.

## Testes de carga: painel e execuÃ§Ã£o automatizada

Os dois modos sÃ£o independentes. A API deve estar rodando em outro terminal;
nenhum dos iniciadores de carga inicia ou encerra a API. Use uma conta de teste
e seu `access_token` vÃ¡lido, sem incluir o prefixo `Bearer` ao informar o token.
As rotas de perfil e tarefas exigem JWT; token expirado ou invÃ¡lido gera falhas.

### Fluxo atual pelo painel â€” preservado

```powershell
.\iniciar_teste_carga.bat
```

Solicita o token conforme o comportamento anterior e abre o Locust usando
`load_tests/locustfile.py`. No painel do navegador, configure usuÃ¡rios, entrada
por segundo e duraÃ§Ã£o, clique em START e acompanhe os resultados. Esse BAT,
o locustfile e os arquivos de carga dos alunos nÃ£o foram modificados.

### Novo fluxo automatizado â€” sem painel

```powershell
.\iniciar_teste_carga_aut.bat
```

Reutiliza `.venv\Scripts\python.exe`, instala Locust caso ausente e solicita
`TASKLAB_TOKEN` com entrada visÃ­vel no terminal se a variÃ¡vel nÃ£o estiver definida. Depois
executa automaticamente, em sequÃªncia e em processos separados:

1. `GET /users/me`, com relatÃ³rio `load_tests_automatizados/relatorios/perfil.html`.
2. `GET /tasks`, com relatÃ³rio `load_tests_automatizados/relatorios/tarefas.html`.

Para executar somente uma rota:

```powershell
.\iniciar_teste_carga_aut.bat perfil
```

Executa somente `GET /users/me` e atualiza apenas o relatÃ³rio `perfil.html`.

```powershell
.\iniciar_teste_carga_aut.bat tarefas
```

Executa somente `GET /tasks` e atualiza apenas o relatÃ³rio `tarefas.html`.
Um parÃ¢metro invÃ¡lido mostra as opÃ§Ãµes aceitas e encerra sem executar a carga.

Os testes sÃ£o descobertos automaticamente pelos arquivos `carga_*.py` na pasta
`load_tests_automatizados`, em ordem alfabÃ©tica. Para adicionar um cenÃ¡rio,
crie, por exemplo, `carga_estatisticas.py` com sua classe de usuÃ¡rio, carga e
critÃ©rios. Ele poderÃ¡ ser executado com:

```powershell
.\iniciar_teste_carga_aut.bat estatisticas
```

Esse comando funciona depois de criar o arquivo. NÃ£o Ã© necessÃ¡rio cadastrar
a rota no executor nem usar tags: o nome do arquivo identifica o teste.
O endpoint Ã© definido dentro do prÃ³prio arquivo de carga.

Sem parÃ¢metro, todos os arquivos encontrados sÃ£o executados, mesmo se um anterior reprovar ou apresentar erro.
Os relatÃ³rios de mesmo nome sÃ£o substituÃ­dos na prÃ³xima execuÃ§Ã£o; o diretÃ³rio
Ã© criado automaticamente e os arquivos gerados sÃ£o ignorados pelo Git.
O token Ã© transmitido pelo ambiente e no cabeÃ§alho Authorization das requisiÃ§Ãµes,
sem aparecer nos argumentos de processo ou nos relatÃ³rios gerados. Ao informar
o token manualmente, ele fica visÃ­vel no terminal.

### ConfiguraÃ§Ã£o e critÃ©rios

Cada arquivo (`carga_perfil.py` e `carga_tarefas.py`) possui seus prÃ³prios
parÃ¢metros. NÃ£o hÃ¡ mais um mÃ³dulo `configuracao.py`. Os valores iniciais sÃ£o:

- Meta: **1000 usuÃ¡rios simultÃ¢neos**.
- Entrada: **20 usuÃ¡rios por segundo**, controlada por `LoadTestShape`.
- DuraÃ§Ã£o: **60 segundos por rota, incluindo a entrada gradual**.
- Espera entre tarefas: `between(1, 2)` segundos.
- Host: `http://127.0.0.1:8000`.
- Timeout por requisiÃ§Ã£o: 10 segundos.

Em condiÃ§Ãµes normais, a entrada atÃ© 1000 usuÃ¡rios leva aproximadamente 50 segundos;
o restante dos 60 segundos mantÃ©m a carga. A duraÃ§Ã£o nÃ£o Ã© 60 segundos adicionais
apÃ³s atingir a meta. O tempo de iniciar processos e gerar relatÃ³rios Ã© adicional.
Cada arquivo de rota define sua prÃ³pria classe `CargaAutomatizada`.
Altere `usuarios`, `entrada_por_segundo` e `duracao_segundos` nessa classe
para configurar somente aquele cenÃ¡rio. Na classe de usuÃ¡rio do mesmo arquivo,
ajuste `host`, `wait_time = between(1, 2)` e o `timeout=10` da requisiÃ§Ã£o.
O executor nÃ£o sobrescreve o host nem a duraÃ§Ã£o definidos em cada teste.
Nenhuma estatÃ­stica Ã© reiniciada ao terminar a entrada gradual.

Cada arquivo de carga possui sua prÃ³pria funÃ§Ã£o `avaliar_resultado`.
Os limites ficam no inÃ­cio do arquivo, em `P95_MAXIMO_MS` e
`FALHAS_MAXIMAS_PERCENTUAL`, e podem ser diferentes para cada rota.
NÃ£o hÃ¡ mais um mÃ³dulo `criterios.py`. A aprovaÃ§Ã£o ocorre somente quando:

- HÃ¡ pelo menos uma requisiÃ§Ã£o executada.
- p95 da execuÃ§Ã£o inteira Ã© **menor ou igual a 500 ms**.
- Percentual de falhas Ã© **menor ou igual a 1%**.
- NÃ£o ocorreram exceÃ§Ãµes nas tarefas nem erros internos identificados pelo Locust.

Cada requisiÃ§Ã£o deve retornar HTTP 200. Outros status, redirecionamentos e erros
de conexÃ£o sÃ£o registrados como falhas, sem incluir corpo ou cabeÃ§alhos nos erros.
O percentual Ã© calculado por `falhas / requisiÃ§Ãµes * 100`; a decisÃ£o usa o valor
sem arredondar, embora o resumo mostre duas casas decimais. O p95 usa o histograma
de tempos do Locust para toda a execuÃ§Ã£o, nÃ£o apenas a janela recente.

Durante cada teste, o terminal atualiza apenas o tempo decorrido na mesma linha.
Esse tempo inclui a inicializaÃ§Ã£o do Locust e a geraÃ§Ã£o do relatÃ³rio.
As tabelas periÃ³dicas do Locust nÃ£o sÃ£o exibidas.
Ao terminar cada rota, o terminal mostra requisiÃ§Ãµes, falhas, percentual de falhas,
p95, exceÃ§Ãµes e **APROVADO/REPROVADO**. O executor apresenta um resumo final:
cÃ³digo de saÃ­da 0 somente se todas as rotas selecionadas passarem e gerarem relatÃ³rio; diferente de 0
se qualquer uma reprovar ou apresentar erro. O executor aguarda cada processo
terminar; a duraÃ§Ã£o da carga Ã© controlada pelo `LoadTestShape` de cada arquivo.

### Arquivos do novo modo

| Arquivo | Responsabilidade |
| --- | --- |
| `carga_perfil.py` | Consulta de perfil, parÃ¢metros de carga e critÃ©rios de aprovaÃ§Ã£o. |
| `carga_tarefas.py` | Listagem de tarefas, parÃ¢metros de carga e critÃ©rios de aprovaÃ§Ã£o. |
| `executar_carga.py` | Descobre `carga_*.py` e executa o selecionado ou todos em sequÃªncia. |
| `relatorios/` | RelatÃ³rios HTML separados, gerados pelo Locust. |
| `iniciar_teste_carga_aut.bat` | Prepara o ambiente e chama o executor. |

Ã‰ possÃ­vel conferir a descoberta das classes sem iniciar a carga:

```powershell
.\.venv\Scripts\python.exe -m locust -f load_tests_automatizados/carga_perfil.py --list
.\.venv\Scripts\python.exe -m locust -f load_tests_automatizados/carga_tarefas.py --list
```

Esses comandos apenas carregam os arquivos e listam seus usuÃ¡rios; nÃ£o fazem
requisiÃ§Ãµes nem geram relatÃ³rios de desempenho. A implementaÃ§Ã£o foi conferida
com Locust 2.47.0, sem executar a carga completa de 1000 usuÃ¡rios.
