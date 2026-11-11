import os
from locust import HttpUser, between, task, tag


class UsuarioTaskLab(HttpUser):
    wait_time = between(1, 2)

    def _headers(self):
        return {
            "Authorization": f"Bearer {os.environ['TASKLAB_TOKEN']}"
        }

    @tag("perfil")
    @task
    def consultar_perfil(self):
        self.client.get("/users/me", headers=self._headers())

    @tag("listar_tarefas")
    @task
    def listar_tarefas(self):
        self.client.get("/tasks", headers=self._headers())

    @tag("estatisticas_tarefas")
    @task
    def consultar_estatisticas_tarefas(self):
        self.client.get("/tasks/stats", headers=self._headers())

    @tag("consultar_tarefa")
    @task
    def consultar_tarefa(self):
        task_id = os.environ.get("TASKLAB_TASK_ID")
        if not task_id:
            raise RuntimeError(
                "Defina TASKLAB_TASK_ID com o ID de uma tarefa da conta do token."
            )
        self.client.get(f"/tasks/{task_id}", headers=self._headers())
