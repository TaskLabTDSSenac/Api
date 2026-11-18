import os
import uuid

from locust import HttpUser, between, task, tag


class UsuarioTaskLab(HttpUser):
    wait_time = between(1, 2)

    def on_start(self):
        token = os.environ.get("TASKLAB_TOKEN", "").strip()
        if not token:
            raise RuntimeError(
                "TASKLAB_TOKEN não definido. Exporte um JWT Bearer válido antes de iniciar o Locust."
            )

        self.headers = {"Authorization": f"Bearer {token}"}
        self.task_id = None
        self._criar_tarefa_auxiliar()

    def _criar_tarefa_auxiliar(self):
        """Cria uma tarefa pendente para as operações que precisam de ID."""
        payload = {
            "title": f"preparacao-{uuid.uuid4().hex}",
            "description": "Tarefa auxiliar criada para o teste de carga.",
        }
        with self.client.post(
            "/tasks",
            name="POST /tasks [preparação]",
            json=payload,
            headers=self.headers,
            catch_response=True,
        ) as response:
            if response.status_code != 201:
                response.failure(
                    f"Esperado HTTP 201 ao preparar tarefa; recebido HTTP {response.status_code}"
                )
                self.task_id = None
            else:
                self.task_id = response.json().get("id")

        if self.task_id is None:
            raise RuntimeError("Não foi possível criar tarefa auxiliar com ID para este usuário.")

    def _garantir_tarefa(self):
        if self.task_id is None:
            self._criar_tarefa_auxiliar()

    @tag("perfil")
    @task
    def consultar_perfil(self):
        with self.client.get(
            "/users/me",
            name="/users/me",
            headers=self.headers,
            catch_response=True,
        ) as response:
            if response.status_code != 200:
                response.failure(f"Esperado HTTP 200; recebido HTTP {response.status_code}")

    @tag("criar")
    @task
    def criar_tarefa(self):
        payload = {
            "title": f"carga-{uuid.uuid4().hex}",
            "description": "Tarefa criada durante o teste de carga.",
        }
        with self.client.post(
            "/tasks",
            name="POST /tasks",
            json=payload,
            headers=self.headers,
            catch_response=True,
        ) as response:
            if response.status_code != 201:
                response.failure(f"Esperado HTTP 201; recebido HTTP {response.status_code}")

    @tag("listar")
    @task
    def listar_tarefas(self):
        with self.client.get(
            "/tasks",
            name="GET /tasks",
            headers=self.headers,
            catch_response=True,
        ) as response:
            if response.status_code != 200:
                response.failure(f"Esperado HTTP 200; recebido HTTP {response.status_code}")

    @tag("estatisticas")
    @task
    def consultar_estatisticas(self):
        with self.client.get(
            "/tasks/stats",
            name="GET /tasks/stats",
            headers=self.headers,
            catch_response=True,
        ) as response:
            if response.status_code != 200:
                response.failure(f"Esperado HTTP 200; recebido HTTP {response.status_code}")

    @tag("consultar")
    @task
    def consultar_tarefa(self):
        self._garantir_tarefa()
        with self.client.get(
            f"/tasks/{self.task_id}",
            name="/tasks/{id}",
            headers=self.headers,
            catch_response=True,
        ) as response:
            if response.status_code != 200:
                response.failure(f"Esperado HTTP 200; recebido HTTP {response.status_code}")

    @tag("editar")
    @task
    def editar_tarefa(self):
        self._garantir_tarefa()
        payload = {
            "title": f"editada-{uuid.uuid4().hex}",
            "description": "Tarefa atualizada durante o teste de carga.",
        }
        with self.client.put(
            f"/tasks/{self.task_id}",
            name="/tasks/{id}",
            json=payload,
            headers=self.headers,
            catch_response=True,
        ) as response:
            if response.status_code != 200:
                response.failure(f"Esperado HTTP 200; recebido HTTP {response.status_code}")

    @tag("concluir")
    @task
    def concluir_tarefa(self):
        self._garantir_tarefa()
        with self.client.patch(
            f"/tasks/{self.task_id}/complete",
            name="/tasks/{id}/complete",
            headers=self.headers,
            catch_response=True,
        ) as response:
            if response.status_code == 200:
                # A próxima chamada de conclusão precisa de uma tarefa pendente nova.
                self.task_id = None
            else:
                response.failure(f"Esperado HTTP 200; recebido HTTP {response.status_code}")
