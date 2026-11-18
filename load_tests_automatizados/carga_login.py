from __future__ import annotations

import os

from pathlib import Path

from locust import HttpUser, between, events, task
from locust.env import Environment
from locust.html import get_html_report

# Credenciais de um usuário dedicado a testes, fornecidas pelo ambiente.
BASE_URL = os.environ.get("LOGIN_BASE_URL", "http://127.0.0.1:8000").rstrip("/")
TEST_EMAIL = os.environ.get("LOGIN_TEST_EMAIL", "").strip()
TEST_PASSWORD = os.environ.get("LOGIN_TEST_PASSWORD", "")
REPORT_PATH = Path(os.environ.get("LOGIN_REPORT_PATH", "load_tests_automatizados/relatorio_login.html"))

# Carga moderada para o custo de verificação do hash de senha.
USERS = int(os.environ.get("LOGIN_USERS", "20"))
SPAWN_RATE = float(os.environ.get("LOGIN_SPAWN_RATE", "2"))
RUN_TIME = os.environ.get("LOGIN_RUN_TIME", "1m")

MAX_FAILURE_PERCENT = 1.0
MAX_AVERAGE_MS = 800.0
MAX_P95_MS = 1500.0
MIN_REQUESTS_PER_SECOND = 2.0


class UsuarioLogin(HttpUser):
    host = BASE_URL
    wait_time = between(1, 2)

    def on_start(self):
        if not TEST_EMAIL or not TEST_PASSWORD:
            raise RuntimeError(
                "Configure LOGIN_TEST_EMAIL e LOGIN_TEST_PASSWORD com credenciais "
                "de um usuário de teste válido."
            )

    @task
    def login(self):
        with self.client.post(
            "/auth/login",
            name="POST /auth/login",
            json={"email": TEST_EMAIL, "password": TEST_PASSWORD},
            catch_response=True,
        ) as response:
            if response.status_code != 200:
                response.failure(f"Esperado HTTP 200; recebido HTTP {response.status_code}")
                return
            try:
                payload = response.json()
            except ValueError:
                response.failure("Resposta não contém JSON válido")
                return
            if not payload.get("access_token") or payload.get("token_type") != "bearer":
                response.failure("Resposta não contém access_token/token_type bearer válidos")


def evaluate(stats) -> tuple[bool, list[str]]:
    total = stats.total
    if total.num_requests == 0:
        return False, ["Nenhuma requisição de login foi concluída"]

    failure_percent = total.fail_ratio * 100
    average_ms = total.avg_response_time
    p95_ms = total.get_response_time_percentile(0.95) or 0
    throughput = total.current_rps
    reasons = []
    if failure_percent > MAX_FAILURE_PERCENT:
        reasons.append(f"falhas {failure_percent:.2f}% > {MAX_FAILURE_PERCENT:.2f}%")
    if average_ms > MAX_AVERAGE_MS:
        reasons.append(f"média {average_ms:.0f} ms > {MAX_AVERAGE_MS:.0f} ms")
    if p95_ms > MAX_P95_MS:
        reasons.append(f"p95 {p95_ms:.0f} ms > {MAX_P95_MS:.0f} ms")
    if throughput < MIN_REQUESTS_PER_SECOND:
        reasons.append(f"throughput {throughput:.2f} req/s < {MIN_REQUESTS_PER_SECOND:.2f} req/s")
    return not reasons, reasons


@events.test_stop.add_listener
def create_report(environment: Environment, **kwargs):
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text(get_html_report(environment), encoding="utf-8")

    passed, reasons = evaluate(environment.stats)
    total = environment.stats.total
    p95_ms = total.get_response_time_percentile(0.95) or 0
    print("\nCritérios do teste de login:")
    print(f"  Requisições: {total.num_requests}; falhas: {total.fail_ratio * 100:.2f}%")
    print(f"  Resposta média: {total.avg_response_time:.0f} ms; p95: {p95_ms:.0f} ms")
    print(f"  Throughput: {total.current_rps:.2f} req/s")
    print(f"  Relatório HTML: {REPORT_PATH.resolve()}")
    if passed:
        print("RESULTADO: APROVADO")
    else:
        print("RESULTADO: REPROVADO — " + "; ".join(reasons))
        environment.process_exit_code = 1


@events.init.add_listener
def validate_configuration(environment: Environment, **kwargs):
    if USERS < 1 or SPAWN_RATE <= 0:
        raise ValueError("LOGIN_USERS deve ser >= 1 e LOGIN_SPAWN_RATE deve ser > 0")





@events.init_command_line_parser.add_listener
def set_load_defaults(parser, **kwargs):
    parser.set_defaults(num_users=USERS, spawn_rate=SPAWN_RATE, run_time=RUN_TIME, headless=True)


