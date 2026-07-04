"""Service layer for the user management module."""

from __future__ import annotations

from datetime import datetime, timezone

from app.models import User
from app.modules.user_management.models import (
    UserManagementAuditEvent,
    UserManagementProfile,
    UserManagementRoleAssignment,
)
from app.modules.user_management.repository import UserManagementRepository
from app.modules.user_management.schemas import (
    UserManagementAuditEventCreate,
    UserManagementProfileCreate,
    UserManagementProfileUpdate,
    UserManagementRoleAssignmentCreate,
    UserManagementRoleAssignmentUpdate,
)


class UserManagementService:
    """Business boundary for user management operations."""

    def __init__(self, repository: UserManagementRepository) -> None:
        self.repository = repository

    def health(self) -> dict[str, str]:
        return {"status": "ok"}

    def list_users(self) -> list[User]:
        return self.repository.users.list()

    def list_active_users(self) -> list[User]:
        return self.repository.users.list_active()

    def get_user(self, user_id: int) -> User | None:
        return self.repository.users.get_by_id(user_id)

    def require_user(self, user_id: int) -> User:
        return self._require_user(user_id)

    def list_profiles(self) -> list[UserManagementProfile]:
        return self.repository.profiles.list()

    def list_active_profiles(self) -> list[UserManagementProfile]:
        return self.repository.profiles.list_active()

    def get_profile(self, profile_id: int) -> UserManagementProfile | None:
        return self.repository.profiles.get_by_id(profile_id)

    def get_profile_by_user_id(
        self,
        user_id: int,
    ) -> UserManagementProfile | None:
        return self.repository.profiles.get_by_user_id(user_id)

    def create_profile(
        self,
        payload: UserManagementProfileCreate,
    ) -> UserManagementProfile:
        self._validate_profile_user(payload.user_id)
        self._validate_unique_profile_user(payload.user_id)

        profile = UserManagementProfile(
            user_id=payload.user_id,
            display_name=payload.display_name,
            personnel_number=payload.personnel_number,
            job_title=payload.job_title,
            phone_number=payload.phone_number,
            is_active=payload.is_active,
            notes=payload.notes,
        )
        return self.repository.profiles.create(profile)

    def update_profile(
        self,
        profile_id: int,
        payload: UserManagementProfileUpdate,
    ) -> UserManagementProfile | None:
        values: dict[str, object] = payload.model_dump(exclude_unset=True)

        if "user_id" in values:
            user_id = values["user_id"]
            if not isinstance(user_id, int):
                raise ValueError("Invalid profile user")
            self._validate_profile_user(user_id)
            self._validate_unique_profile_user(user_id, profile_id)

        return self.repository.profiles.update(profile_id, values)

    def list_role_assignments(self) -> list[UserManagementRoleAssignment]:
        return self.repository.role_assignments.list()

    def list_active_role_assignments(self) -> list[UserManagementRoleAssignment]:
        return self.repository.role_assignments.list_active()

    def list_user_role_assignments(
        self,
        user_id: int,
    ) -> list[UserManagementRoleAssignment]:
        return self.repository.role_assignments.list_by_user_id(user_id)

    def list_active_user_role_assignments(
        self,
        user_id: int,
    ) -> list[UserManagementRoleAssignment]:
        return self.repository.role_assignments.list_active_by_user_id(user_id)

    def get_role_assignment(
        self,
        role_assignment_id: int,
    ) -> UserManagementRoleAssignment | None:
        return self.repository.role_assignments.get_by_id(role_assignment_id)

    def assign_role(
        self,
        payload: UserManagementRoleAssignmentCreate,
    ) -> UserManagementRoleAssignment:
        self._validate_role_assignment_user(payload.user_id)
        if payload.is_active:
            self._validate_unique_active_role_scope(
                payload.user_id,
                payload.role_code,
                payload.scope_type,
                payload.scope_id,
            )

        role_assignment = UserManagementRoleAssignment(
            user_id=payload.user_id,
            role_code=payload.role_code,
            scope_type=payload.scope_type,
            scope_id=payload.scope_id,
            is_active=payload.is_active,
            assigned_by_user_id=payload.assigned_by_user_id,
        )
        return self.repository.role_assignments.create(role_assignment)

    def create_role_assignment(
        self,
        payload: UserManagementRoleAssignmentCreate,
    ) -> UserManagementRoleAssignment:
        return self.assign_role(payload)

    def update_role_assignment(
        self,
        role_assignment_id: int,
        payload: UserManagementRoleAssignmentUpdate,
    ) -> UserManagementRoleAssignment | None:
        role_assignment = self.repository.role_assignments.get_by_id(
            role_assignment_id,
        )
        if role_assignment is None:
            return None

        values: dict[str, object] = payload.model_dump(exclude_unset=True)
        user_id = role_assignment.user_id
        role_code = role_assignment.role_code
        scope_type = role_assignment.scope_type
        scope_id = role_assignment.scope_id
        is_active = role_assignment.is_active

        if "user_id" in values:
            value = values["user_id"]
            if not isinstance(value, int):
                raise ValueError("Invalid role assignment user")
            self._validate_role_assignment_user(value)
            user_id = value

        if "role_code" in values:
            value = values["role_code"]
            if not isinstance(value, str):
                raise ValueError("Invalid role code")
            role_code = value

        if "scope_type" in values:
            value = values["scope_type"]
            if value is not None and not isinstance(value, str):
                raise ValueError("Invalid role assignment scope type")
            scope_type = value

        if "scope_id" in values:
            value = values["scope_id"]
            if value is not None and not isinstance(value, int):
                raise ValueError("Invalid role assignment scope")
            scope_id = value

        if "is_active" in values:
            value = values["is_active"]
            if not isinstance(value, bool):
                raise ValueError("Invalid role assignment active state")
            is_active = value

        if is_active:
            self._validate_unique_active_role_scope(
                user_id,
                role_code,
                scope_type,
                scope_id,
                role_assignment_id,
            )

        return self.repository.role_assignments.update(role_assignment_id, values)

    def revoke_role_assignment(
        self,
        role_assignment_id: int,
        payload: UserManagementRoleAssignmentUpdate | None = None,
    ) -> UserManagementRoleAssignment | None:
        if self.repository.role_assignments.get_by_id(role_assignment_id) is None:
            return None

        values: dict[str, object] = {}
        if payload is not None:
            values = payload.model_dump(exclude_unset=True)

        values["is_active"] = False
        if values.get("revoked_at") is None:
            values["revoked_at"] = datetime.now(timezone.utc)

        return self.repository.role_assignments.revoke(role_assignment_id, values)

    def list_audit_events(self) -> list[UserManagementAuditEvent]:
        return self.repository.audit_events.list()

    def get_audit_event(
        self,
        audit_event_id: int,
    ) -> UserManagementAuditEvent | None:
        return self.repository.audit_events.get_by_id(audit_event_id)

    def list_audit_events_by_actor(
        self,
        actor_user_id: int,
    ) -> list[UserManagementAuditEvent]:
        return self.repository.audit_events.list_by_actor_user_id(actor_user_id)

    def list_audit_events_by_target(
        self,
        target_user_id: int,
    ) -> list[UserManagementAuditEvent]:
        return self.repository.audit_events.list_by_target_user_id(target_user_id)

    def create_audit_event(
        self,
        payload: UserManagementAuditEventCreate,
    ) -> UserManagementAuditEvent:
        if payload.actor_user_id is not None:
            self._require_user(payload.actor_user_id)
        if payload.target_user_id is not None:
            self._require_user(payload.target_user_id)

        audit_event = UserManagementAuditEvent(
            actor_user_id=payload.actor_user_id,
            target_user_id=payload.target_user_id,
            event_type=payload.event_type,
            summary=payload.summary,
            details=payload.details,
        )
        return self.repository.audit_events.create(audit_event)

    def _require_user(self, user_id: int) -> User:
        user = self.repository.users.get_by_id(user_id)
        if user is None:
            raise ValueError("User not found")
        return user

    def _validate_profile_user(self, user_id: int) -> None:
        self._require_user(user_id)

    def _validate_unique_profile_user(
        self,
        user_id: int,
        profile_id: int | None = None,
    ) -> None:
        existing_profile = self.repository.profiles.get_by_user_id(user_id)
        if existing_profile is not None and existing_profile.id != profile_id:
            raise ValueError("User profile already exists")

    def _validate_role_assignment_user(self, user_id: int) -> None:
        self._require_user(user_id)

    def _validate_unique_active_role_scope(
        self,
        user_id: int,
        role_code: str,
        scope_type: str | None,
        scope_id: int | None,
        role_assignment_id: int | None = None,
    ) -> None:
        for existing_assignment in self.repository.role_assignments.list_by_user_id(
            user_id,
        ):
            if existing_assignment.id == role_assignment_id:
                continue
            if not existing_assignment.is_active:
                continue
            if (
                existing_assignment.role_code == role_code
                and existing_assignment.scope_type == scope_type
                and existing_assignment.scope_id == scope_id
            ):
                raise ValueError("Active role assignment already exists")
