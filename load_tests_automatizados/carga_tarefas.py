"""Mede o desempenho da listagem autenticada de tarefas do usuário."""

import os

from locust import HttpUser, LoadTestShape, between, events, log, task


# A listagem consulta e serializa várias linhas no banco; a carga é menor que
# a do perfil para representar concorrência sustentada sem criar/alterar dados.
P95_MAXIMO_MS = 500
MEDIA_MAXIMA_MS = 250
MAXIMO_MAXIMO_MS = 2_000
FALHAS_MAXIMAS_PERCENTUAL = 1.0


class UsuarioTarefas(HttpUser):
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


class CargaAutomatizada(LoadTestShape):
    usuarios = 100
    entrada_por_segundo = 10
    duracao_segundos = 60

    def tick(self):
        # Os 60 segundos incluem o ramp-up, com até 10s para chegar a 100 usuários.
        if self.get_run_time() >= self.duracao_segundos:
            return None
        return self.usuarios, self.entrada_por_segundo


@events.quitting.add_listener
def avaliar_resultado(environment, **kwargs):
    dados = environment.stats.total
    percentual_falhas = dados.fail_ratio * 100
    media = dados.avg_response_time
    maximo = dados.max_response_time
    p95 = dados.get_response_time_percentile(0.95) if dados.num_requests else 0
    houve_excecoes = bool(environment.runner.exceptions)

    aprovado = (
        dados.num_requests > 0
        and percentual_falhas <= FALHAS_MAXIMAS_PERCENTUAL
        and media <= MEDIA_MAXIMA_MS
        and maximo <= MAXIMO_MAXIMO_MS
        and p95 <= P95_MAXIMO_MS
        and not houve_excecoes
        and not log.unhandled_greenlet_exception
        and environment.process_exit_code in (None, 0)
    )

    print("\nGET /tasks")
    print(f"Requisicoes: {dados.num_requests}")
    print(f"Falhas: {dados.num_failures} ({percentual_falhas:.2f}%)")
    print(f"Tempo medio: {media:.2f} ms (limite: {MEDIA_MAXIMA_MS} ms)")
    print(f"Tempo maximo: {maximo:.2f} ms (limite: {MAXIMO_MAXIMO_MS} ms)")
    print(f"p95: {p95:.2f} ms (limite: {P95_MAXIMO_MS} ms)")
    print(f"Excecoes nas tarefas: {'sim' if houve_excecoes else 'nao'}")
    print("APROVADO" if aprovado else "REPROVADO")
    environment.process_exit_code = 0 if aprovado else 1


@events.init.add_listener
def manter_estatisticas(environment, **kwargs):
    # Inclui as requisições feitas durante a entrada gradual.
    environment.reset_stats = False
