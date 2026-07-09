"""Service layer for the Monitoring & Health module."""

from __future__ import annotations

from app.modules.monitoring_health.repository import MonitoringHealthRepository
from app.modules.monitoring_health.schemas import MonitoringHealthHealthRead


class MonitoringHealthService:
    """Business boundary for health checks and operational diagnostics."""

    def __init__(
        self,
        repository: MonitoringHealthRepository | None = None,
    ) -> None:
        self.repository = repository or MonitoringHealthRepository()

    def health(self) -> MonitoringHealthHealthRead:
        return MonitoringHealthHealthRead(
            module="monitoring_health",
            status="ok" if self.repository.health() else "error",
        )
