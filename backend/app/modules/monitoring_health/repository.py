"""Repository scaffold for the Monitoring & Health module."""

from __future__ import annotations


class MonitoringHealthRepository:
    """Persistence boundary for monitoring and health checks."""

    def health(self) -> bool:
        return True
