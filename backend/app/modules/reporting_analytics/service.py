"""Service layer for the Reporting & Analytics module."""

from .repository import ReportingAnalyticsRepository


class ReportingAnalyticsService:
    """Service boundary for reporting and analytics operations."""

    def __init__(
        self,
        repository: ReportingAnalyticsRepository | None = None,
    ) -> None:
        self.repository = repository or ReportingAnalyticsRepository()

    def health(self) -> dict[str, str]:
        """Return service health status."""
        repository_health = self.repository.health()

        if repository_health.get("status") != "healthy":
            return {"status": "unhealthy", "module": "reporting_analytics"}

        return {"status": "healthy", "module": "reporting_analytics"}
