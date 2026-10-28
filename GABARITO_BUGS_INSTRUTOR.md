# TaskLab — material reservado ao instrutor

## Isolamento e execução

Por solicitação posterior do instrutor, a API está na branch `main`, com as
alterações locais não commitadas. Os clientes foram ajustados nas pastas reais
`TaskLab\Site` e `TaskLab\App`. A cópia temporária anterior não é utilizada.
README e ajustes locais anteriores de inicialização foram preservados.
Nenhum commit ou push foi realizado. As mudanças estão não commitadas e podem
acompanhar uma troca de branch: guarde-as antes de retornar à main, conforme
o procedimento no final deste documento. A main não recebeu commits com defeitos.

Por solicitação do instrutor, a aplicação usa o banco principal `tasklab.db`.
O `iniciar.bat` seleciona esse banco na raiz da API. Os defeitos intencionais
continuam ativos e operam sobre os registros desse banco. Nenhum dado foi
migrado ou apagado durante a troca da configuração.
O gabarito não é servido pela API nem copiado para
Web/Mobile. Não publique esta pasta inteira em um servidor estático para alunos.

Para reutilizar o ambiente Python já instalado, encerre a API original com
Ctrl+C e execute em um novo PowerShell (porta 8000 preserva os clientes atuais):

```powershell
$pythonTaskLab = 'C:\Users\Remakker\Desktop\Instrutor TI Senac\Desenvolvimento de Sistemas\TaskLab\Api\.venv\Scripts\python.exe'
Set-Location 'C:\Users\Remakker\Desktop\Instrutor TI Senac\Desenvolvimento de Sistemas\TaskLab\Api'
$env:DATABASE_URL = 'sqlite:///tasklab.db'
$env:JWT_SECRET_KEY = & $pythonTaskLab -c 'import secrets; print(secrets.token_hex(32))'
& $pythonTaskLab -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

Use `http://127.0.0.1:8000/docs` para requisições diretas e o Flutter Web na
porta 5501. O emulador Android usa `http://10.0.2.2:8000`.
A chave acima é exclusiva desta sessão: faça login novamente no laboratório.
O `iniciar.bat` alternativo prepara uma `.venv` local caso ela ainda não exista;
o comando acima evita essa instalação adicional.

## Preparação dos casos

Cadastre Ana com `POST /auth/register`:
`{"name":"Ana Teste","email":"ana@example.com","password":"SenhaSegura123"}`.
Faça `POST /auth/login` com o e-mail e a senha. Copie `access_token` para
Authorize no Swagger. Todas as operações de tarefas exigem esse token.
Use uma tarefa nova por caso; anote seu ID real, sem assumir que será 1.
Para verificar isolamento, repita o cadastro/login com Bia e outro e-mail fictício.

## Casos e resultados

### BUG-01 — senha de 6 ou 7 caracteres (introduzido)

Envie `POST /auth/register` com nome `Aluno Teste`, e-mail fictício único e
`password` igual a `123456`; repita com outro e-mail e `1234567`.
Correto: 422, pois a senha deve ter pelo menos 8 caracteres.
Observado: 201; o login aceita a senha cadastrada. O hash continua Argon2,
e a senha incorreta continua retornando 401. Senhas ausentes, vazias, de 5 ou
mais de 128 caracteres continuam rejeitadas.
Nas telas de cadastro Web e Mobile, informe senha de 6 ou 7 caracteres e preencha
a confirmação. O envio é permitido. Faça login usando a senha principal.
O limite da troca de senha continua sendo 8 caracteres: BUG-01 é de cadastro.

### BUG-02 — confirmação divergente (introduzido nos clientes)

Não existe campo de confirmação no contrato da API. Enviar `confirm_password`
divergente em `/auth/register` continua retornando 422 por campo extra.
Web e Mobile agora exigem confirmação preenchida, mas não comparam seu valor.
No cadastro, informe senha `SenhaSegura123` e confirmação `OutraSenha456`.
Correto: bloquear o envio. Observado: cadastro aceito com a senha principal.
A API continua recebendo apenas nome, e-mail e senha, sem novo contrato.
Na tela Alterar senha, informe a senha atual correta, nova senha `NovaSenha456`
e confirmação `Diferente789`: a alteração também é enviada e usa `NovaSenha456`.
Essa extensão para troca de senha atende ao exemplo solicitado pelo instrutor.

### BUG-03 — nome com 2 caracteres (preexistente, não introduzido)

Cadastre `{"name":"Al","email":"al@example.com","password":"SenhaSegura123"}`.
Correto segundo o requisito desta atividade: 422, mínimo de 3 caracteres.
Observado: 201, tanto na versão original quanto no laboratório. API, Web e
Mobile já adotam mínimo de 1 caractere após trim. É uma divergência do requisito
da atividade em relação à implementação anterior, não uma regressão nova.
Nenhuma validação do nome foi alterada; o caso é observável também nas interfaces.

### BUG-04 — título só de espaços (introduzido)

Envie `POST /tasks` com `{"title":"   "}`.
Correto: 422, pois o título deve ter entre 3 e 150 caracteres após trim.
Observado: 201, título contendo os três espaços persistido, descrição null e
completed false. Confirme por `GET /tasks/{id}` e `GET /tasks`.
Título ausente, vazio, de 2 letras ou acima de 150 caracteres continua rejeitado
na criação. A edição ainda rejeita título só de espaços.
Nas telas de criação Web e Mobile, digite três espaços no título e salve.
Os espaços são enviados sem trim; a tarefa aparece na lista com título em branco.

### BUG-05 — descrição não atualizada (introduzido)

Crie `{"title":"Tarefa original","description":"Descricao original"}`.
Envie `PUT /tasks/{id}` com
`{"title":"Titulo atualizado","description":"Nova descricao"}`.
Correto: 200 com ambos os campos atualizados e persistidos.
Observado: 200 com título novo, mas descrição antiga; um GET posterior e uma
nova sessão de banco confirmam a descrição anterior. Omitir description também
não a limpa. Reproduzível no formulário de edição Web/Mobile; reabra a tarefa.

### BUG-06 — conclusão repetida (introduzido)

Crie uma tarefa válida. Envie `PATCH /tasks/{id}/complete` duas vezes.
Correto: primeira resposta 200; segunda 400, tarefa já concluída.
Observado: ambas 200 com completed true. A autenticação e a propriedade
continuam verificadas em ambas as requisições.
O botão Concluir permanece disponível nos dois clientes após a conclusão.
Conclua uma tarefa, aguarde o retorno e clique novamente: a segunda operação
também informa sucesso. Não é necessário abrir duas telas nem usar o Swagger.

### BUG-07 — exclusão sem remoção (introduzido)

Crie uma tarefa válida; envie `DELETE /tasks/{id}`.
Correto: 204 vazio, seguido de GET por ID com 404 e ausência na listagem.
Observado: 204 vazio, mas GET retorna 200 e o registro permanece na lista e
no banco. Nas interfaces, exclua e recarregue a listagem para observar o retorno.
ID inexistente ou de outra conta continua retornando 404.

### BUG-08 — edição com título longo (introduzido)

Crie uma tarefa válida; envie `PUT /tasks/{id}` com title contendo 151 letras
`x` consecutivas. Pode gerar o texto no PowerShell com `'x' * 151`.
Correto: 422 e manutenção do título anterior.
Observado: 200, as 151 letras são persistidas. SQLite não impõe o limite do
tipo String(150); nenhuma mudança de estrutura do banco foi necessária.
O limite de 500 caracteres da descrição e o limite de título na criação
continuam ativos. Nas telas de edição Web e Mobile, cole um título de 151 letras
e salve. O contador ainda mostra o limite esperado de 150, mas o envio é aceito.
Reabra os detalhes para conferir o título persistido. Na criação, o limite de
150 continua sendo aplicado: este defeito é exclusivo da edição.

## Verificação manual

Por solicitação do instrutor, os testes automatizados e suas configurações foram
removidos dos projetos. A implementação de testes em código ficará para uma
etapa futura. Os casos descritos neste gabarito devem ser executados manualmente
pelas interfaces. Resultados automatizados mencionados anteriormente são históricos;
as suítes correspondentes não estão mais presentes no projeto.

Para carregar os ajustes, atualize o Site com Ctrl+F5 e faça Hot Restart no
Flutter; se usar um APK instalado, gere e instale uma nova versão.

Arquivos do Site alterados: `cadastro.html`, `perfil.html`, `js/register.js`,
`js/profile.js`, `js/task-form.js`, `js/tasks.js`, `js/task-details.js`.
Arquivos do App alterados: `lib/models/validators.dart`,
`lib/screens/register_screen.dart`, `lib/screens/change_password_screen.dart`,
`lib/screens/task_form_screen.dart`, `lib/services/task_service.dart`,
`lib/widgets/task_actions.dart`.

## Retorno à versão original

Encerre o Uvicorn do laboratório com Ctrl+C e feche o PowerShell usado acima.
Em um novo terminal, na pasta `TaskLab\Api`, guarde as alterações dos três
repositórios. O procedimento guarda também outros ajustes locais não commitados:

```powershell
git stash push -u -m "TaskLab laboratorio e alteracoes locais preservadas"
git -C ../Site stash push -u -m "TaskLab clientes laboratorio"
git -C ../App stash push -u -m "TaskLab clientes laboratorio"
git switch main
.\iniciar.bat
```

O stash também guarda as alterações locais anteriores de README e iniciar.bat;
não as descarte. Arquivos ignorados, como `.env`, `.venv` e bancos, ficam intactos.
Para retomar o laboratório, com a API parada e a árvore de trabalho limpa:

```powershell
git stash list
# Identifique o stash com a mensagem acima; use seu índice correto.
git stash apply 'stash@{0}'
git -C ../Site stash list
git -C ../Site stash apply 'stash@{0}'
git -C ../App stash list
git -C ../App stash apply 'stash@{0}'
.\iniciar.bat
```

Ao reaplicar os stashes, os defeitos voltam aos arquivos locais, inclusive na
main conforme solicitado pelo instrutor. Reinicie o Flutter e recarregue o Site.
Faça login novamente nos clientes. Confirme o índice de cada stash antes de aplicar.
