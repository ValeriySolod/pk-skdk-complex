from __future__ import annotations

from typing import Generic, TypeVar

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.base import Base


ModelT = TypeVar("ModelT", bound=Base)


class BaseRepository(Generic[ModelT]):
    """Generic repository for small SQLAlchemy ORM persistence operations."""

    def __init__(self, session: Session, model: type[ModelT]) -> None:
        """Store the database session and ORM model handled by the repository."""
        self.session = session
        self.model = model

    def get(self, id: object) -> ModelT | None:
        """Return one model instance by primary key, or None when absent."""
        return self.session.get(self.model, id)

    def list(self) -> list[ModelT]:
        """Return all model instances for the repository model."""
        return list(self.session.scalars(select(self.model)).all())

    def add(self, instance: ModelT) -> ModelT:
        """Add a model instance to the current unit of work."""
        self.session.add(instance)
        return instance

    def delete(self, instance: ModelT) -> None:
        """Mark a model instance for deletion in the current unit of work."""
        self.session.delete(instance)

    def refresh(self, instance: ModelT) -> ModelT:
        """Refresh a model instance from the database and return it."""
        self.session.refresh(instance)
        return instance
