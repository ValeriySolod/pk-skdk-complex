from app.models import User
from app.modules.user_management.repository import UserManagementRepository


class UserManagementService:
    def __init__(self, repository: UserManagementRepository) -> None:
        self.repository = repository

    def health(self) -> dict[str, str]:
        return {"status": "ok"}

    def list_users(self) -> list[User]:
        return self.repository.list_users()

    def get_user(self, user_id: int) -> User | None:
        return self.repository.get_user(user_id)
