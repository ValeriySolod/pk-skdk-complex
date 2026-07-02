from sqlalchemy.orm import Session

from app.models import AuditLog
from app.repositories.base import BaseRepository


class AuditLogRepository(BaseRepository[AuditLog]):
    """Repository for audit log persistence operations."""

    def __init__(self, session: Session) -> None:
        """Create an audit log repository bound to a database session."""
        super().__init__(session, AuditLog)
