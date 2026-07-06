"""Reporting & Analytics module registration."""

from fastapi import APIRouter

from app.core.module_registry import ModuleManifest, registry

from .models import (
    AnalyticsSnapshot,
    AnalyticsSnapshotPeriod,
    AnalyticsSnapshotStatus,
    DashboardDefinition,
    DashboardStatus,
    ReportDefinition,
    ReportDefinitionStatus,
    ReportOutputFormat,
    ReportRun,
    ReportRunStatus,
)
from .routes import router


def get_router() -> APIRouter:
    return router


registry.register(
    ModuleManifest(
        code="reporting-analytics",
        title="Reporting & Analytics",
        description="Dashboards, analytics snapshots, and printable/exportable reports.",
        router_factory=get_router,
        permissions=["reporting_analytics:read"],
    )
)


__all__ = [
    "AnalyticsSnapshot",
    "AnalyticsSnapshotPeriod",
    "AnalyticsSnapshotStatus",
    "DashboardDefinition",
    "DashboardStatus",
    "ReportDefinition",
    "ReportDefinitionStatus",
    "ReportOutputFormat",
    "ReportRun",
    "ReportRunStatus",
    "get_router",
]
