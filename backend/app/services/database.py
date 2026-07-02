from dataclasses import dataclass

from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session


@dataclass(frozen=True)
class DatabaseHealthStatus:
    status: str
    database: str
    detail: str | None = None

    @property
    def is_healthy(self) -> bool:
        return self.status == "ok"

    def as_response(self) -> dict[str, str]:
        response = {
            "status": self.status,
            "database": self.database,
        }
        if self.detail is not None:
            response["detail"] = self.detail
        return response


class DatabaseHealthService:
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
