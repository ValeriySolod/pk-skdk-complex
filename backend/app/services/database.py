from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.services.health import ServiceHealthStatus


class DatabaseHealthStatus(ServiceHealthStatus):
    """Health status payload for database connectivity checks."""

    def __init__(self, status: str, database: str, detail: str | None = None) -> None:
        super().__init__(
            status=status,
            component_key="database",
            component_status=database,
            detail=detail,
        )

    @property
    def database(self) -> str:
        return self.component_status


class DatabaseHealthService:
    """Run database health checks."""

    def __init__(self, db: Session) -> None:
        self.db = db

    def check_connection(self) -> DatabaseHealthStatus:
        try:
            self.db.execute(text("SELECT 1"))
        except SQLAlchemyError:
            return DatabaseHealthStatus(
                status="unhealthy",
                database="disconnected",
                detail="Database connection check failed",
            )

        return DatabaseHealthStatus(status="ok", database="connected")
