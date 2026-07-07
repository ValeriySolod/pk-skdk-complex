"""System Settings module registration."""

from app.core.module_registry import registry

from .manifest import get_router, manifest
from .models import (
    SystemSetting,
    SystemSettingAuditEvent,
    SystemSettingChangeAction,
    SystemSettingChangeEvent,
    SystemSettingDefault,
    SystemSettingDefaultStatus,
    SystemSettingStatus,
    SystemSettingValueType,
)

registry.register(manifest)

__all__ = [
    "SystemSetting",
    "SystemSettingAuditEvent",
    "SystemSettingChangeAction",
    "SystemSettingChangeEvent",
    "SystemSettingDefault",
    "SystemSettingDefaultStatus",
    "SystemSettingStatus",
    "SystemSettingValueType",
    "get_router",
    "manifest",
]
