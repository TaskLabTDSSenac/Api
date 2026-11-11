import os

from locust import HttpUser, between, task, tag


class UsuarioTaskLab(HttpUser):
    wait_time = between(1, 2)

    def on_start(self):
        token = os.getenv("TASKLAB_TOKEN")
        if not token:
            raise RuntimeError("Defina a variavel de ambiente TASKLAB_TOKEN antes de iniciar o Locust.")
        self.headers = {"Authorization": f"Bearer {token}"}

    @tag("perfil")
    @task(3)
    def consultar_perfil(self):
        self.client.get("/users/me", headers=self.headers, name="GET /users/me")

    @tag("tarefas")
    @task(5)
    def listar_tarefas(self):
        self.client.get("/tasks", headers=self.headers, name="GET /tasks")

    @tag("estatisticas")
    @task(2)
    def consultar_estatisticas(self):
        self.client.get("/tasks/stats", headers=self.headers, name="GET /tasks/stats")