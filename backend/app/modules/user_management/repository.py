"""Repository skeletons for the user management module."""

from __future__ import annotations

from collections.abc import Mapping

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import User
from app.modules.user_management.models import (
    UserManagementAuditEvent,
    UserManagementProfile,
    UserManagementRoleAssignment,
)


class UserManagementUserRepository:
    """Read-only persistence operations for core auth users."""

    def __init__(self, db: Session) -> None:
        self.db = db

    def get_by_id(self, user_id: int) -> User | None:
        return self.db.get(User, user_id)

    def list(self) -> list[User]:
        return list(self.db.scalars(select(User).order_by(User.id)).all())

    def list_active(self) -> list[User]:
        return list(
            self.db.scalars(
                select(User).where(User.is_active.is_(True)).order_by(User.id),
            ).all(),
        )


class UserManagementProfileRepository:
    """Persistence operations for administrative user profiles."""

    def __init__(self, db: Session) -> None:
        self.db = db

    def get_by_id(self, profile_id: int) -> UserManagementProfile | None:
        return self.db.get(UserManagementProfile, profile_id)

    def get_by_user_id(self, user_id: int) -> UserManagementProfile | None:
        return self.db.scalar(
            select(UserManagementProfile).where(UserManagementProfile.user_id == user_id),
        )

    def list(self) -> list[UserManagementProfile]:
        return list(
            self.db.scalars(
                select(UserManagementProfile).order_by(UserManagementProfile.id),
            ).all(),
        )

    def list_active(self) -> list[UserManagementProfile]:
        return list(
            self.db.scalars(
                select(UserManagementProfile)
                .where(UserManagementProfile.is_active.is_(True))
                .order_by(UserManagementProfile.id),
            ).all(),
        )

    def create(
        self,
        profile: UserManagementProfile,
    ) -> UserManagementProfile:
        self.db.add(profile)
        self.db.flush()
        return profile

    def update(
        self,
        profile_id: int,
        values: Mapping[str, object],
    ) -> UserManagementProfile | None:
        profile = self.get_by_id(profile_id)
        if profile is None:
            return None

        for field, value in values.items():
            setattr(profile, field, value)

        self.db.flush()
        return profile


class UserManagementRoleAssignmentRepository:
    """Persistence operations for user role assignments."""

    def __init__(self, db: Session) -> None:
        self.db = db

    def get_by_id(
        self,
        role_assignment_id: int,
    ) -> UserManagementRoleAssignment | None:
        return self.db.get(UserManagementRoleAssignment, role_assignment_id)

    def list(self) -> list[UserManagementRoleAssignment]:
        return list(
            self.db.scalars(
                select(UserManagementRoleAssignment).order_by(
                    UserManagementRoleAssignment.id,
                ),
            ).all(),
        )

    def list_active(self) -> list[UserManagementRoleAssignment]:
        return list(
            self.db.scalars(
                select(UserManagementRoleAssignment)
                .where(UserManagementRoleAssignment.is_active.is_(True))
                .order_by(UserManagementRoleAssignment.id),
            ).all(),
        )

    def list_by_user_id(self, user_id: int) -> list[UserManagementRoleAssignment]:
        return list(
            self.db.scalars(
                select(UserManagementRoleAssignment)
                .where(UserManagementRoleAssignment.user_id == user_id)
                .order_by(UserManagementRoleAssignment.id),
            ).all(),
        )

    def list_active_by_user_id(
        self,
        user_id: int,
    ) -> list[UserManagementRoleAssignment]:
        return list(
            self.db.scalars(
                select(UserManagementRoleAssignment)
                .where(
                    UserManagementRoleAssignment.user_id == user_id,
                    UserManagementRoleAssignment.is_active.is_(True),
                )
                .order_by(UserManagementRoleAssignment.id),
            ).all(),
        )

    def get_by_scope(
        self,
        user_id: int,
        role_code: str,
        scope_type: str | None,
        scope_id: int | None,
    ) -> UserManagementRoleAssignment | None:
        return self.db.scalar(
            select(UserManagementRoleAssignment).where(
                UserManagementRoleAssignment.user_id == user_id,
                UserManagementRoleAssignment.role_code == role_code,
                UserManagementRoleAssignment.scope_type == scope_type,
                UserManagementRoleAssignment.scope_id == scope_id,
            ),
        )

    def create(
        self,
        role_assignment: UserManagementRoleAssignment,
    ) -> UserManagementRoleAssignment:
        self.db.add(role_assignment)
        self.db.flush()
        return role_assignment

    def update(
        self,
        role_assignment_id: int,
        values: Mapping[str, object],
    ) -> UserManagementRoleAssignment | None:
        role_assignment = self.get_by_id(role_assignment_id)
        if role_assignment is None:
            return None

        for field, value in values.items():
            setattr(role_assignment, field, value)

        self.db.flush()
        return role_assignment

    def revoke(
        self,
        role_assignment_id: int,
        values: Mapping[str, object],
    ) -> UserManagementRoleAssignment | None:
        return self.update(role_assignment_id, values)


class UserManagementAuditEventRepository:
    """Persistence operations for user management audit events."""

    def __init__(self, db: Session) -> None:
        self.db = db

    def get_by_id(self, audit_event_id: int) -> UserManagementAuditEvent | None:
        return self.db.get(UserManagementAuditEvent, audit_event_id)

    def list(self) -> list[UserManagementAuditEvent]:
        return list(
            self.db.scalars(
                select(UserManagementAuditEvent).order_by(
                    UserManagementAuditEvent.id.desc(),
                ),
            ).all(),
        )

    def list_by_actor_user_id(
        self,
        actor_user_id: int,
    ) -> list[UserManagementAuditEvent]:
        return list(
            self.db.scalars(
                select(UserManagementAuditEvent)
                .where(UserManagementAuditEvent.actor_user_id == actor_user_id)
                .order_by(UserManagementAuditEvent.id.desc()),
            ).all(),
        )

    def list_by_target_user_id(
        self,
        target_user_id: int,
    ) -> list[UserManagementAuditEvent]:
        return list(
            self.db.scalars(
                select(UserManagementAuditEvent)
                .where(UserManagementAuditEvent.target_user_id == target_user_id)
                .order_by(UserManagementAuditEvent.id.desc()),
            ).all(),
        )

    def create(
        self,
        audit_event: UserManagementAuditEvent,
    ) -> UserManagementAuditEvent:
        self.db.add(audit_event)
        self.db.flush()
        return audit_event


class UserManagementRepository:
    """Aggregate access point for user management repositories."""

    def __init__(self, db: Session) -> None:
        self.db = db
        self.users = UserManagementUserRepository(db)
        self.profiles = UserManagementProfileRepository(db)
        self.role_assignments = UserManagementRoleAssignmentRepository(db)
        self.audit_events = UserManagementAuditEventRepository(db)

    def list_users(self) -> list[User]:
        return self.users.list()

    def get_user(self, user_id: int) -> User | None:
        return self.users.get_by_id(user_id)


__all__ = [
    "UserManagementAuditEventRepository",
    "UserManagementProfileRepository",
    "UserManagementRepository",
    "UserManagementRoleAssignmentRepository",
    "UserManagementUserRepository",
]
