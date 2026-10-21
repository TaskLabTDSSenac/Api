from app.models.task import Task
from app.repositories.task_repository import TaskRepository
from app.schemas.task_schema import TaskCreate


class TaskService:
    def __init__(self, repository: TaskRepository):
        self.repository = repository

    def create_task(self, user_id: int, data: TaskCreate) -> Task:
        return self.repository.create(user_id, data.title, data.description)

    def list_tasks(self, user_id: int) -> list[Task]:
        return self.repository.list_by_user(user_id)
