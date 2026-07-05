"""Service layer skeleton for the notifications module."""

from __future__ import annotations

from app.modules.notifications.repository import NotificationsRepository


class NotificationsService:
    """Business boundary for notification workflows."""

    def __init__(self, repository: NotificationsRepository) -> None:
        self.repository = repository

    def health(self) -> dict[str, str]:
        status = "ok" if self.repository.health() else "degraded"
        return {"status": status}


__all__ = ["NotificationsService"]
