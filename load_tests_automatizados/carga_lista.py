import os

from locust import HttpUser, LoadTestShape, between, events, log, task


P95_MAXIMO_MS = 500
FALHAS_MAXIMAS_PERCENTUAL = 1.0


class UsuarioLista(HttpUser):
    host = "http://127.0.0.1:8000"
    wait_time = between(1, 2)

    def on_start(self):
        token = os.environ["TASKLAB_TOKEN"].strip()
        self.client.headers.update({"Authorization": f"Bearer {token}"})

    @task
    def listar_tarefas(self):
        with self.client.get(
            "/tasks", name="/tasks", timeout=10,
            catch_response=True, allow_redirects=False,
        ) as resposta:
            if resposta.status_code != 200:
                resposta.failure(f"HTTP inesperado: {resposta.status_code}; esperado: 200.")
            else:
                try:
                    corpo = resposta.json()
                except ValueError:
                    resposta.failure("Corpo inesperado; esperado uma lista JSON.")
                else:
                    if not isinstance(corpo, list):
                        resposta.failure("Corpo inesperado; esperado uma lista JSON.")


class CargaAutomatizada(LoadTestShape):
    usuarios = 300
    entrada_por_segundo = 30
    duracao_segundos = 60

    def tick(self):
        if self.get_run_time() >= self.duracao_segundos:
            return None
        return self.usuarios, self.entrada_por_segundo


@events.quitting.add_listener
def avaliar_resultado(environment, **kwargs):
    dados = environment.stats.total
    percentual_falhas = dados.fail_ratio * 100
    p95 = dados.get_response_time_percentile(0.95) if dados.num_requests else 0
    houve_excecoes = bool(environment.runner.exceptions)

    aprovado = (
        dados.num_requests > 0
        and p95 <= P95_MAXIMO_MS
        and percentual_falhas <= FALHAS_MAXIMAS_PERCENTUAL
        and not houve_excecoes
        and not log.unhandled_greenlet_exception
        and environment.process_exit_code in (None, 0)
    )

    print("\nGET /tasks (listagem)")
    print(f"Requisicoes: {dados.num_requests}")
    print(f"Falhas: {dados.num_failures} ({percentual_falhas:.2f}%)")
    print(f"p95: {p95:.2f} ms")
    print(f"Excecoes nas tarefas: {'sim' if houve_excecoes else 'nao'}")
    print("APROVADO" if aprovado else "REPROVADO")
    environment.process_exit_code = 0 if aprovado else 1


@events.init.add_listener
def manter_estatisticas(environment, **kwargs):
    environment.reset_stats = False
