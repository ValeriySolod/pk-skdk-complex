"""Audit Log module registration."""

from app.core.module_registry import registry
from app.modules.audit_log.models import AuditLogEvent

from .manifest import get_router, manifest

registry.register(manifest)


__all__ = ["AuditLogEvent", "get_router", "manifest"]
