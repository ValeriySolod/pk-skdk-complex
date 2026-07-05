"""Repository skeleton for the audit log module."""

from __future__ import annotations

from sqlalchemy.orm import Session


class AuditLogRepository:
    """Persistence boundary for future audit log storage operations."""

    def __init__(self, db: Session) -> None:
        self.db = db


__all__ = ["AuditLogRepository"]
