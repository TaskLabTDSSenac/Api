import os
from locust import HttpUser, between, task, tag


class UsuarioTaskLab(HttpUser):
    wait_time = between(1, 2)

    @tag("perfil")
    @task
    def consultar_perfil(self):
        self.client.get(
            "/users/me",
            headers={
                "Authorization": f"Bearer {os.environ['TASKLAB_TOKEN']}"
            },
        )

    @tag("tarefas")
    @task
    def consultar_tarefas(self):
        self.client.get(
            "/tasks",
            headers={
                "Authorization": f"Bearer {os.environ['TASKLAB_TOKEN']}"
            },
        )

    @tag("estatisticas")
    @task
    def consultar_estatisticas_tarefas(self):
        self.client.get(
            "/tasks/stats",
            headers={
                "Authorization": f"Bearer {os.environ['TASKLAB_TOKEN']}"
            },
        )

    @tag("tarefas_concluidas")
    @task
    def consultar_tarefas_concluidas(self):
        self.client.get(
            "/tasks",
            params={"completed": "true"},
            headers={
                "Authorization": f"Bearer {os.environ['TASKLAB_TOKEN']}"
            },
        )
