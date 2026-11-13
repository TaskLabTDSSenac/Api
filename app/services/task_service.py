from app.models.task import Task
from app.exceptions import TaskNotFoundError
from app.repositories.task_repository import TaskRepository
from app.schemas.task_schema import TaskCreate, TaskStatsResponse, TaskUpdate


class TaskService:
    def __init__(self, repository: TaskRepository):
        self.repository = repository

    def create_task(self, user_id: int, data: TaskCreate) -> Task:
        return self.repository.create(user_id, data.title, data.description)

    def list_tasks(
        self, user_id: int, completed: bool | None = None, search: str | None = None,
    ) -> list[Task]:
        search = search.strip() if search is not None else None
        return self.repository.list_by_user(user_id, completed, search or None)

    def get_stats(self, user_id: int) -> TaskStatsResponse:
        total, pending, completed = self.repository.count_by_user(user_id)
        percentage = round((completed / total) * 100, 2) if total else 0.0
        return TaskStatsResponse(
            total=total, pending=pending, completed=completed,
            completion_percentage=percentage,
        )

    def get_task(self, user_id: int, task_id: int) -> Task:
        task = self.repository.get_by_id_and_user(task_id, user_id)
        if task is None:
            raise TaskNotFoundError()
        return task

    def update_task(self, user_id: int, task_id: int, data: TaskUpdate) -> Task:
        task = self.get_task(user_id, task_id)
        task.title = data.title
        return self.repository.save(task)

    def complete_task(self, user_id: int, task_id: int) -> Task:
        task = self.get_task(user_id, task_id)
        task.completed = True
        return self.repository.save(task)

    def delete_task(self, user_id: int, task_id: int) -> None:
        self.get_task(user_id, task_id)
