from fastapi import APIRouter

from app.core.module_registry import ModuleManifest, registry
from app.modules.user_management.models import (
    UserManagementAuditEvent,
    UserManagementProfile,
    UserManagementRoleAssignment,
)

from .routes import router


def get_router() -> APIRouter:
    return router


registry.register(
    ModuleManifest(
        code="user-management",
        title="User Management",
        description="User CRUD, role assignment, and permissions management.",
        router_factory=get_router,
        permissions=["user_management:read"],
    )
)


__all__ = [
    "UserManagementAuditEvent",
    "UserManagementProfile",
    "UserManagementRoleAssignment",
]
