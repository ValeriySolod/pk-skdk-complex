from sqlalchemy.orm import Session

from app.models import Organization
from app.repositories.base import BaseRepository


class OrganizationRepository(BaseRepository[Organization]):
    """Repository for organization persistence operations."""

    def __init__(self, session: Session) -> None:
        """Create an organization repository bound to a database session."""
        super().__init__(session, Organization)
