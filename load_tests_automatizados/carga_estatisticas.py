import json
import os

from locust import HttpUser, LoadTestShape, between, events, log, task


P95_MAXIMO_MS = 500
FALHAS_MAXIMAS_PERCENTUAL = 1.0


class UsuarioEstatisticas(HttpUser):
    host = "http://127.0.0.1:8000"
    wait_time = between(1, 2)

    def on_start(self):
        token = os.environ["TASKLAB_TOKEN"].strip()
        self.client.headers.update({"Authorization": f"Bearer {token}"})

    @task
    def consultar_estatisticas(self):
        with self.client.get(
            "/tasks/stats", name="/tasks/stats", timeout=10,
            catch_response=True, allow_redirects=False,
        ) as resposta:
            if resposta.status_code != 200:
                resposta.failure(f"HTTP inesperado: {resposta.status_code}; esperado: 200.")
                return

            try:
                dados = resposta.json()
            except (json.JSONDecodeError, ValueError):
                resposta.failure("Resposta não contém JSON válido.")
                return

            campos = {"total", "pending", "completed", "completion_percentage"}
            if not isinstance(dados, dict) or not campos.issubset(dados):
                resposta.failure("Resposta não contém os campos de estatísticas esperados.")
                return

            total = dados["total"]
            pendentes = dados["pending"]
            concluidas = dados["completed"]
            percentual = dados["completion_percentage"]
            contagens_validas = all(
                isinstance(valor, int) and not isinstance(valor, bool) and valor >= 0
                for valor in (total, pendentes, concluidas)
            )
            percentual_esperado = round(concluidas / total * 100, 2) if total else 0.0

            if (
                not contagens_validas
                or pendentes + concluidas != total
                or not isinstance(percentual, (int, float))
                or isinstance(percentual, bool)
                or percentual != percentual_esperado
            ):
                resposta.failure("Valores de estatísticas inconsistentes.")


class CargaAutomatizada(LoadTestShape):
    usuarios = 60
    entrada_por_segundo = 12
    duracao_segundos = 45

    def tick(self):
        # A duração inclui a entrada gradual dos usuários.
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

    print("\nGET /tasks/stats")
    print(f"Requisicoes: {dados.num_requests}")
    print(f"Falhas: {dados.num_failures} ({percentual_falhas:.2f}%)")
    print(f"p95: {p95:.2f} ms")
    print(f"Excecoes nas tarefas: {'sim' if houve_excecoes else 'nao'}")
    print("APROVADO" if aprovado else "REPROVADO")
    environment.process_exit_code = 0 if aprovado else 1


@events.init.add_listener
def manter_estatisticas(environment, **kwargs):
    # Inclui as requisições feitas durante a entrada gradual.
    environment.reset_stats = False
