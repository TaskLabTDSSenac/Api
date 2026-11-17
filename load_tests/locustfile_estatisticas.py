import os

from locust import HttpUser, between, task


class TesteEstatisticas(HttpUser):
    wait_time = between(1, 2)

    def on_start(self):
        token = os.getenv("TASKLAB_TOKEN")
        if not token:
            raise RuntimeError("Defina a variavel de ambiente TASKLAB_TOKEN antes de iniciar o Locust.")
        self.headers = {"Authorization": f"Bearer {token}"}

    @task
    def consultar_estatisticas(self):
        self.client.get("/tasks/stats", headers=self.headers, name="GET /tasks/stats")
