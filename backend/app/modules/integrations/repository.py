"""Repository boundary for the Integrations module."""

from __future__ import annotations


class IntegrationsRepository:
    """Persistence boundary reserved for future integration data."""

    def health(self) -> bool:
        """Return skeleton repository availability."""

        return True


__all__ = ["IntegrationsRepository"]
