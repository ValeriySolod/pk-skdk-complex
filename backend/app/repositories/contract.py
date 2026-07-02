from sqlalchemy.orm import Session

from app.models import Contract
from app.repositories.base import BaseRepository


class ContractRepository(BaseRepository[Contract]):
    """Repository for contract persistence operations."""

    def __init__(self, session: Session) -> None:
        """Create a contract repository bound to a database session."""
        super().__init__(session, Contract)
