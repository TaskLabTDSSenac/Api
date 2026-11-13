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