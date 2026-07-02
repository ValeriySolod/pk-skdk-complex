from sqlalchemy.orm import Session

from app.models import Shipment
from app.repositories.base import BaseRepository


class ShipmentRepository(BaseRepository[Shipment]):
    """Repository for shipment persistence operations."""

    def __init__(self, session: Session) -> None:
        """Create a shipment repository bound to a database session."""
        super().__init__(session, Shipment)
