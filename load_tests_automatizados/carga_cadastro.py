import uuid

from locust import HttpUser, LoadTestShape, between, events, log, task


P95_MAXIMO_MS = 1000
FALHAS_MAXIMAS_PERCENTUAL = 1.0


class UsuarioCadastro(HttpUser):
    """Simula novos usuários criando uma conta com dados inéditos."""

    host = "http://127.0.0.1:8000"
    wait_time = between(1, 2)

    @task
    def cadastrar_usuario(self):
        dados = {
            "name": "Usuario Carga",
            "email": f"carga-{uuid.uuid4().hex}@example.com",
            "password": "SenhaCarga123",
        }
        with self.client.post(
            "/auth/register",
            json=dados,
            name="POST /auth/register",
            timeout=10,
            catch_response=True,
            allow_redirects=False,
        ) as resposta:
            if resposta.status_code != 201:
                resposta.failure(
                    f"HTTP inesperado: {resposta.status_code}; esperado: 201."
                )


class CargaAutomatizada(LoadTestShape):
    usuarios = 5
    entrada_por_segundo = 1
    duracao_segundos = 40

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

    print("\nPOST /auth/register")
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
