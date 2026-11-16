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
    @tag("CT-12")
    @task
    def ct12_listar_tarefas(self):
        with self.client.get(
            "/tasks",
            headers={"Authorization": f"Bearer {os.environ['TASKLAB_TOKEN']}"},
            name="CT-12 GET /tasks",
            catch_response=True,
        ) as resposta:
            if resposta.status_code != 200:
                resposta.failure(f"Esperava HTTP 200, recebeu {resposta.status_code}")
                return
            try:
                tarefas = resposta.json()
            except ValueError:
                resposta.failure("A resposta não contém JSON válido")
                return
            if not isinstance(tarefas, list):
                resposta.failure("A resposta deveria ser uma lista de tarefas")

    @tag("CT-13")
    @task
    def ct13_listar_tarefas_concluidas(self):
        with self.client.get(
            "/tasks",
            params={"completed": "true"},
            headers={"Authorization": f"Bearer {os.environ['TASKLAB_TOKEN']}"},
            name="CT-13 GET /tasks?completed=true",
            catch_response=True,
        ) as resposta:
            if resposta.status_code != 200:
                resposta.failure(f"Esperava HTTP 200, recebeu {resposta.status_code}")
                return
            try:
                tarefas = resposta.json()
            except ValueError:
                resposta.failure("A resposta não contém JSON válido")
                return
            if not isinstance(tarefas, list):
                resposta.failure("A resposta deveria ser uma lista de tarefas")
            elif any(tarefa.get("completed") is not True for tarefa in tarefas):
                resposta.failure("A listagem contém tarefa não concluída")

    @tag("CT-14")
    @task
    def ct14_listar_tarefas_pendentes(self):
        with self.client.get(
            "/tasks",
            params={"completed": "false"},
            headers={"Authorization": f"Bearer {os.environ['TASKLAB_TOKEN']}"},
            name="CT-14 GET /tasks?completed=false",
            catch_response=True,
        ) as resposta:
            if resposta.status_code != 200:
                resposta.failure(f"Esperava HTTP 200, recebeu {resposta.status_code}")
                return
            try:
                tarefas = resposta.json()
            except ValueError:
                resposta.failure("A resposta não contém JSON válido")
                return
            if not isinstance(tarefas, list):
                resposta.failure("A resposta deveria ser uma lista de tarefas")
            elif any(tarefa.get("completed") is not False for tarefa in tarefas):
                resposta.failure("A listagem contém tarefa concluída")
