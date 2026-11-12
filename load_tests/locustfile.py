import os

from locust import HttpUser, between, task, tag


class UsuarioTaskLabFelipe(HttpUser):
    wait_time = between(1, 2)

    def on_start(self):
        self.headers = {
            "Authorization": f"Bearer {os.environ['TASKLAB_TOKEN']}"
        }

    @tag("listar_tarefas")
    @task
    def listar_tarefas(self):
        self.client.get("/tasks", headers=self.headers)

    @tag("estatisticas_tarefas")
    @task
    def consultar_estatisticas_tarefas(self):
        self.client.get("/tasks/stats", headers=self.headers)

    @tag("health")
    @task
    def verificar_health(self):
        self.client.get("/health")

    @tag("perfil")
    @task
    def consultar_perfil(self):
        self.client.get("/users/me" )
