"""Service layer skeleton for the audit log module."""

from __future__ import annotations

from app.modules.audit_log.repository import AuditLogRepository


class AuditLogService:
    """Business boundary for future audit log operations."""

    def __init__(self, repository: AuditLogRepository) -> None:
        self.repository = repository

    def health(self) -> dict[str, str]:
        return {"status": "ok"}
