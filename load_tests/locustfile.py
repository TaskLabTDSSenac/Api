import os
from locust import HttpUser, between, task, tag


class UsuarioTaskLab(HttpUser):
    host = "http://127.0.0.1:8000"
    wait_time = between(1, 2)

    def on_start(self):
        token = os.environ["TASKLAB_TOKEN"].strip()
        self.client.headers.update({"Authorization": f"Bearer {token}"})

    @tag("perfil")
    @task
    def consultar_perfil(self):
        with self.client.get(
            "/users/me",
            name="GET /users/me",
            timeout=10,
            catch_response=True,
        ) as resposta:
            if resposta.status_code != 200:
                resposta.failure(
                    f"HTTP inesperado: {resposta.status_code}; esperado: 200."
                )

    @tag("infra")
    @task
    def verificar_saude(self):
        with self.client.get(
            "/health",
            name="GET /health",
            timeout=10,
            catch_response=True,
        ) as resposta:
            if resposta.status_code != 200:
                resposta.failure(
                    f"HTTP inesperado: {resposta.status_code}; esperado: 200."
                )

    @tag("tarefas", "listagem")
    @task
    def listar_tarefas(self):
        with self.client.get(
            "/tasks",
            name="GET /tasks",
            params={"completed": "false", "search": "teste"},
            timeout=10,
            catch_response=True,
        ) as resposta:
            if resposta.status_code != 200:
                resposta.failure(
                    f"HTTP inesperado: {resposta.status_code}; esperado: 200."
                )

    @tag("tarefas", "estatisticas")
    @task
    def consultar_estatisticas(self):
        with self.client.get(
            "/tasks/stats",
            name="GET /tasks/stats",
            timeout=10,
            catch_response=True,
        ) as resposta:
            if resposta.status_code != 200:
                resposta.failure(
                    f"HTTP inesperado: {resposta.status_code}; esperado: 200."
                )