"""Service layer for the System Settings module."""

from __future__ import annotations

from app.modules.system_settings.repository import SystemSettingsRepository


class SystemSettingsService:
    """Business boundary for configurable application settings and defaults."""

    def __init__(self, repository: SystemSettingsRepository) -> None:
        self.repository = repository

    def health(self) -> dict[str, str]:
        status = "ok" if self.repository.health() else "degraded"
        return {"status": status}
