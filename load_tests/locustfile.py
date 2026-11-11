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

    @tag("tarefas")
    @task
    def listar_tarefas(self):
        self.client.get("/tasks", headers=self._headers())

    @tag("tarefas")
    @task
    def consultar_estatisticas_tarefas(self):
        self.client.get("/tasks/stats", headers=self._headers())

    @tag("tarefas")
    @task
    def consultar_tarefa(self):
        # Obtém um ID válido da própria conta para consultar a rota de detalhe.
        response = self.client.get("/tasks", headers=self._headers())
        if response.ok:
            tarefas = response.json()
            if tarefas:
                self.client.get(
                    f"/tasks/{tarefas[0]['id']}",
                    headers=self._headers(),
                )
