"""Service layer for the Integrations module."""

from __future__ import annotations

from app.modules.integrations.repository import IntegrationsRepository
from app.modules.integrations.schemas import IntegrationsHealthRead


class IntegrationsService:
    """Business boundary for external service connection workflows."""

    def __init__(self, repository: IntegrationsRepository) -> None:
        self.repository = repository

    def health(self) -> IntegrationsHealthRead:
        """Return Integrations module health without provider checks."""

        return IntegrationsHealthRead(
            module="integrations",
            status="ok" if self.repository.health() else "error",
        )


__all__ = ["IntegrationsService"]
