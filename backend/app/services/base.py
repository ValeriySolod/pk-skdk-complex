from __future__ import annotations

from typing import Generic, TypeVar

from app.db.base import Base
from app.repositories.base import BaseRepository


ModelT = TypeVar("ModelT", bound=Base)


class BaseService(Generic[ModelT]):
    """Generic service layer foundation over repository persistence operations."""

    def __init__(self, repository: BaseRepository[ModelT]) -> None:
        """Create a service backed by a repository instance."""
        self.repository = repository

    def get(self, id: object) -> ModelT | None:
        """Return one model instance by primary key, or None when absent."""
        return self.repository.get(id)

    def list(self) -> list[ModelT]:
        """Return all model instances available through the repository."""
        return self.repository.list()

    def add(self, instance: ModelT) -> ModelT:
        """Add a model instance through the repository."""
        return self.repository.add(instance)

    def delete(self, instance: ModelT) -> None:
        """Delete a model instance through the repository."""
        self.repository.delete(instance)

    def refresh(self, instance: ModelT) -> ModelT:
        """Refresh a model instance through the repository."""
        return self.repository.refresh(instance)
