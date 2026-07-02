from sqlalchemy import text
from sqlalchemy.orm import Session


class DatabaseHealthService:
    def __init__(self, db: Session) -> None:
        self.db = db

    def check_connection(self) -> bool:
        self.db.execute(text("SELECT 1"))
        return True
