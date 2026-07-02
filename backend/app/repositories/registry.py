from sqlalchemy.orm import Session

from app.models import Registry
from app.repositories.base import BaseRepository


class RegistryRepository(BaseRepository[Registry]):
    """Repository for registry persistence operations."""

    def __init__(self, session: Session) -> None:
        """Create a registry repository bound to a database session."""
        super().__init__(session, Registry)
