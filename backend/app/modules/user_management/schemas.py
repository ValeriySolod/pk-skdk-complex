from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict


class UserManagementHealthRead(BaseModel):
    status: str


class UserRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    email: str | None = None
    is_active: bool


class UserManagementProfileBase(BaseModel):
    user_id: int
    display_name: str | None = None
    personnel_number: str | None = None
    job_title: str | None = None
    phone_number: str | None = None
    is_active: bool = True
    notes: str | None = None


class UserManagementProfileCreate(UserManagementProfileBase):
    pass


class UserManagementProfileUpdate(BaseModel):
    display_name: str | None = None
    personnel_number: str | None = None
    job_title: str | None = None
    phone_number: str | None = None
    is_active: bool | None = None
    notes: str | None = None


class UserManagementProfileRead(UserManagementProfileBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    updated_at: datetime


class UserManagementRoleAssignmentBase(BaseModel):
    user_id: int
    role_code: str
    scope_type: str | None = None
    scope_id: int | None = None
    is_active: bool = True
    assigned_by_user_id: int | None = None


class UserManagementRoleAssignmentCreate(UserManagementRoleAssignmentBase):
    pass


class UserManagementRoleAssignmentUpdate(BaseModel):
    role_code: str | None = None
    scope_type: str | None = None
    scope_id: int | None = None
    is_active: bool | None = None
    assigned_by_user_id: int | None = None
    revoked_at: datetime | None = None


class UserManagementRoleAssignmentRead(UserManagementRoleAssignmentBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    assigned_at: datetime
    revoked_at: datetime | None = None


class UserManagementAuditEventBase(BaseModel):
    actor_user_id: int | None = None
    target_user_id: int | None = None
    event_type: str
    summary: str | None = None
    details: dict[str, Any] | None = None


class UserManagementAuditEventCreate(UserManagementAuditEventBase):
    pass


class UserManagementAuditEventRead(UserManagementAuditEventBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
