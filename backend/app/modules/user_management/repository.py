from sqlalchemy.orm import Session

from app.models import User


class UserManagementRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def list_users(self) -> list[User]:
        return self.db.query(User).order_by(User.id).all()

    def get_user(self, user_id: int) -> User | None:
        return self.db.get(User, user_id)
