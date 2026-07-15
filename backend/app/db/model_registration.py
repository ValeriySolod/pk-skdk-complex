from __future__ import annotations

from importlib import import_module

from sqlalchemy import MetaData

from app.db.base import Base


MODEL_MODULES = (
    "app.models",
    "app.modules.organization_structure.models",
    "app.modules.user_management.models",
    "app.modules.document_management.models",
    "app.modules.audit_log.models",
    "app.modules.file_storage.models",
    "app.modules.notifications.models",
    "app.modules.reporting_analytics.models",
    "app.modules.administration.models",
    "app.modules.system_settings.models",
    "app.modules.integrations.models",
    "app.modules.backup_restore.models",
    "app.modules.monitoring_health.models",
)


def register_models() -> MetaData:
    """Import every ORM model module and return Alembic's canonical metadata."""
    for module_name in MODEL_MODULES:
        import_module(module_name)
    return Base.metadata
