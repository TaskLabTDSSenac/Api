import os
from locust import HttpUser, between, task, tag

TOKEN = os.environ["TASKLAB_TOKEN"]
MAX_TASKS = int(os.getenv("TASKLAB_MAX_TASKS", "10"))
task_count = 0


class UsuarioTaskLab(HttpUser):
    wait_time = between(1, 2)
    headers = {"Authorization": f"Bearer {TOKEN}"}

    @tag("perfil")
    @task
    def consultar_perfil(self):
        with self.client.get(
            "/users/me", headers=self.headers, catch_response=True
        ) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"HTTP {response.status_code}")

    @tag("tarefas")
    @task
    def criar_tarefa(self):
        global task_count
        if task_count >= MAX_TASKS:
            return

        task_count += 1
        with self.client.post(
            "/tasks",
            json={"title": "atividade123", "description": "professor pediu"},
            headers=self.headers,
            catch_response=True,
        ) as response:
            if response.status_code == 201:
                response.success()
            else:
                response.failure(f"HTTP {response.status_code}")

    @tag("health")
    @task
    def consultar_health(self):
        with self.client.get(
            "/health", name="GET /health", catch_response=True
        ) as response:
            if response.status_code != 200:
                response.failure(f"HTTP {response.status_code}")
                return

            try:
                resultado = response.json()
            except ValueError:
                response.failure("Resposta sem JSON valido")
                return

            if (
                isinstance(resultado, dict)
                and resultado.get("status") == "healthy"
                and resultado.get("database") == "connected"
            ):
                response.success()
            else:
                response.failure("API ou banco nao indicou estado saudavel")
