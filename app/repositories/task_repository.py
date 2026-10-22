from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.models.task import Task
from app.models.user import utc_now


class TaskRepository:
    def __init__(self, session: Session):
        self.session = session

    def get_by_id_and_user(self, task_id: int, user_id: int) -> Task | None:
        return self.session.scalar(
            select(Task).where(Task.id == task_id, Task.user_id == user_id)
        )

    def save(self, task: Task) -> Task:
        try:
            task.updated_at = utc_now()
            self.session.commit()
            self.session.refresh(task)
        except SQLAlchemyError:
            self.session.rollback()
            raise
        return task

    def delete(self, task: Task) -> None:
        try:
            self.session.delete(task)
            self.session.commit()
        except SQLAlchemyError:
            self.session.rollback()
            raise

    def create(self, user_id: int, title: str, description: str | None) -> Task:
        task = Task(user_id=user_id, title=title, description=description, completed=False)
        try:
            self.session.add(task)
            self.session.commit()
            self.session.refresh(task)
        except SQLAlchemyError:
            self.session.rollback()
            raise
        return task

    def list_by_user(self, user_id: int) -> list[Task]:
        statement = (
            select(Task)
            .where(Task.user_id == user_id)
            .order_by(Task.created_at.desc(), Task.id.desc())
        )
        return list(self.session.scalars(statement).all())
