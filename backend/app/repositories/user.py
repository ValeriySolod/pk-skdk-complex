from sqlalchemy.orm import Session

from app.models import User
from app.repositories.base import BaseRepository


class UserRepository(BaseRepository[User]):
    """Repository for user persistence operations."""

    def __init__(self, session: Session) -> None:
        """Create a user repository bound to a database session."""
        super().__init__(session, User)
