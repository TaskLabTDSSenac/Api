from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.models.task import Task


class TaskRepository:
    def __init__(self, session: Session):
        self.session = session

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
