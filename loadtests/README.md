# Testes de carga TaskLab

O Locust está centralizado em `load_tests/locustfile.py`. O arquivo da pasta
`load_tests` também é o usado por `iniciar_teste_carga.bat`. Os CSVs, HTMLs e
banco de teste em `loadtests/results/` são artefatos locais e estão ignorados pelo Git.

A classe oferece estas tasks, todas com peso padrão 1 e espera de 1 a 2 segundos:

- `perfil`: GET /users/me
- `criar`: POST /tasks, com título UUID e descrição
- `listar`: GET /tasks
- `estatisticas`: GET /tasks/stats
- `consultar`: GET /tasks/{id}
- `editar`: PUT /tasks/{id}
- `concluir`: PATCH /tasks/{id}/complete

Todas usam o cabeçalho Bearer guardado em `TASKLAB_TOKEN`. Cada usuário virtual
cria uma tarefa auxiliar no `on_start`; após concluir essa tarefa, cria outra
antes da próxima chamada que precisa de um ID. A preparação também aparece como
`POST /tasks [preparação]` nas métricas. As chamadas de criação de tarefas gravam
dados no banco da API.

## Executar

Na raiz `Api`, configure um JWT válido e rode:

```powershell
$env:TASKLAB_TOKEN = "COLE_AQUI_UM_ACCESS_TOKEN"
.\.venv\Scripts\python.exe -m locust -f load_tests\locustfile.py --host http://127.0.0.1:8000
```

Para executar apenas uma tag, adicione `--tags perfil`, `--tags estatisticas`,
`--tags criar`, `--tags concluir`, `--tags consultar`, `--tags editar` ou
`--tags listar`. O helper de preparação em `loadtests/prepare_data.py` continua
disponível para preparar usuário e seed no banco dedicado.
