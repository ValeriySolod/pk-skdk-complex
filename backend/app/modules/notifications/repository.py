"""Repository skeleton for the notifications module."""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session


class NotificationsRepository:
    """Persistence boundary for notifications data."""

    def __init__(self, db: Session) -> None:
        self.db = db

    def health(self) -> bool:
        return self.db.scalar(select(1)) == 1


__all__ = ["NotificationsRepository"]
