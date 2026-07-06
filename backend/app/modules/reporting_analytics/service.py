"""Service layer for the Reporting & Analytics module."""

from __future__ import annotations

from collections.abc import Mapping
from datetime import datetime
from typing import Any
from uuid import UUID

from app.modules.reporting_analytics.models import (
    AnalyticsSnapshot,
    DashboardDefinition,
    ReportDefinition,
    ReportRun,
)
from app.modules.reporting_analytics.repository import ReportingAnalyticsRepository


class ReportingAnalyticsService:
    """Thin service boundary for reporting and analytics operations."""

    def __init__(
        self,
        repository: ReportingAnalyticsRepository | None = None,
    ) -> None:
        self.repository = repository or ReportingAnalyticsRepository()

    def health(self) -> dict[str, str]:
        """Return service health status."""
        repository_health = self.repository.health()

        if isinstance(repository_health, Mapping):
            repository_status = repository_health.get("status")
            if repository_status != "healthy":
                return {"status": "unhealthy", "module": "reporting_analytics"}
        elif repository_health is not True:
            return {"status": "unhealthy", "module": "reporting_analytics"}

        return {"status": "healthy", "module": "reporting_analytics"}

    # Dashboard definitions

    def create_dashboard(
        self,
        dashboard: DashboardDefinition,
    ) -> DashboardDefinition:
        """Create a dashboard definition."""
        return self._dashboards.create_dashboard(dashboard)

    def get_dashboard_by_id(
        self,
        dashboard_id: int,
        *,
        include_deleted: bool = False,
    ) -> DashboardDefinition | None:
        """Return a dashboard definition by integer ID."""
        return self._dashboards.get_by_id(
            dashboard_id,
            include_deleted=include_deleted,
        )

    def get_dashboard_by_uuid(
        self,
        dashboard_uuid: UUID,
        *,
        include_deleted: bool = False,
    ) -> DashboardDefinition | None:
        """Return a dashboard definition by UUID."""
        return self._dashboards.get_by_uuid(
            dashboard_uuid,
            include_deleted=include_deleted,
        )

    def get_dashboard_by_code(
        self,
        code: str,
        *,
        include_deleted: bool = False,
    ) -> DashboardDefinition | None:
        """Return a dashboard definition by stable code."""
        return self._dashboards.get_by_code(code, include_deleted=include_deleted)

    def list_dashboards(
        self,
        *,
        category: str | None = None,
        status: str | None = None,
        owner_user_id: int | None = None,
        created_from: datetime | None = None,
        created_to: datetime | None = None,
        include_deleted: bool = False,
        limit: int | None = None,
        offset: int | None = None,
    ) -> list[DashboardDefinition]:
        """List dashboard definitions using repository filters."""
        return self._dashboards.list(
            category=category,
            status=status,
            owner_user_id=owner_user_id,
            created_from=created_from,
            created_to=created_to,
            include_deleted=include_deleted,
            limit=limit,
            offset=offset,
        )

    def count_dashboards(
        self,
        *,
        category: str | None = None,
        status: str | None = None,
        owner_user_id: int | None = None,
        created_from: datetime | None = None,
        created_to: datetime | None = None,
        include_deleted: bool = False,
    ) -> int:
        """Count dashboard definitions using repository filters."""
        return self._dashboards.count(
            category=category,
            status=status,
            owner_user_id=owner_user_id,
            created_from=created_from,
            created_to=created_to,
            include_deleted=include_deleted,
        )

    def update_dashboard(
        self,
        dashboard_id: int,
        values: Mapping[str, object],
    ) -> DashboardDefinition | None:
        """Update mutable dashboard definition fields."""
        return self._dashboards.update(dashboard_id, values)

    def delete_dashboard(self, dashboard_id: int) -> bool:
        """Soft-delete a dashboard definition."""
        return self._dashboards.delete(dashboard_id)

    def mark_dashboard_deleted(self, dashboard_id: int) -> bool:
        """Soft-delete a dashboard definition using lifecycle alias."""
        return self._dashboards.mark_deleted(dashboard_id)

    def dashboard_exists(
        self,
        dashboard_id: int,
        *,
        include_deleted: bool = False,
    ) -> bool:
        """Return whether a dashboard definition exists."""
        return self._dashboards.exists(
            dashboard_id,
            include_deleted=include_deleted,
        )

    # Report definitions

    def create_report_definition(
        self,
        report: ReportDefinition,
    ) -> ReportDefinition:
        """Create a report definition."""
        return self._report_definitions.create_report_definition(report)

    def create_report(
        self,
        report: ReportDefinition,
    ) -> ReportDefinition:
        """Create a report definition using a shorter alias."""
        return self.create_report_definition(report)

    def get_report_definition_by_id(
        self,
        report_definition_id: int,
        *,
        include_deleted: bool = False,
    ) -> ReportDefinition | None:
        """Return a report definition by integer ID."""
        return self._report_definitions.get_by_id(
            report_definition_id,
            include_deleted=include_deleted,
        )

    def get_report_by_id(
        self,
        report_definition_id: int,
        *,
        include_deleted: bool = False,
    ) -> ReportDefinition | None:
        """Return a report definition by integer ID using a shorter alias."""
        return self.get_report_definition_by_id(
            report_definition_id,
            include_deleted=include_deleted,
        )

    def get_report_definition_by_uuid(
        self,
        report_uuid: UUID,
        *,
        include_deleted: bool = False,
    ) -> ReportDefinition | None:
        """Return a report definition by UUID."""
        return self._report_definitions.get_by_uuid(
            report_uuid,
            include_deleted=include_deleted,
        )

    def get_report_by_uuid(
        self,
        report_uuid: UUID,
        *,
        include_deleted: bool = False,
    ) -> ReportDefinition | None:
        """Return a report definition by UUID using a shorter alias."""
        return self.get_report_definition_by_uuid(
            report_uuid,
            include_deleted=include_deleted,
        )

    def get_report_definition_by_code(
        self,
        code: str,
        *,
        include_deleted: bool = False,
    ) -> ReportDefinition | None:
        """Return a report definition by stable code."""
        return self._report_definitions.get_by_code(
            code,
            include_deleted=include_deleted,
        )

    def get_report_by_code(
        self,
        code: str,
        *,
        include_deleted: bool = False,
    ) -> ReportDefinition | None:
        """Return a report definition by stable code using a shorter alias."""
        return self.get_report_definition_by_code(
            code,
            include_deleted=include_deleted,
        )

    def list_report_definitions(
        self,
        *,
        category: str | None = None,
        source_module: str | None = None,
        status: str | None = None,
        default_format: str | None = None,
        owner_user_id: int | None = None,
        created_from: datetime | None = None,
        created_to: datetime | None = None,
        include_deleted: bool = False,
        limit: int | None = None,
        offset: int | None = None,
    ) -> list[ReportDefinition]:
        """List report definitions using repository filters."""
        return self._report_definitions.list(
            category=category,
            source_module=source_module,
            status=status,
            default_format=default_format,
            owner_user_id=owner_user_id,
            created_from=created_from,
            created_to=created_to,
            include_deleted=include_deleted,
            limit=limit,
            offset=offset,
        )

    def list_reports(
        self,
        **filters: Any,
    ) -> list[ReportDefinition]:
        """List report definitions using a shorter alias."""
        return self.list_report_definitions(**filters)

    def count_report_definitions(
        self,
        *,
        category: str | None = None,
        source_module: str | None = None,
        status: str | None = None,
        default_format: str | None = None,
        owner_user_id: int | None = None,
        created_from: datetime | None = None,
        created_to: datetime | None = None,
        include_deleted: bool = False,
    ) -> int:
        """Count report definitions using repository filters."""
        return self._report_definitions.count(
            category=category,
            source_module=source_module,
            status=status,
            default_format=default_format,
            owner_user_id=owner_user_id,
            created_from=created_from,
            created_to=created_to,
            include_deleted=include_deleted,
        )

    def count_reports(self, **filters: Any) -> int:
        """Count report definitions using a shorter alias."""
        return self.count_report_definitions(**filters)

    def update_report_definition(
        self,
        report_definition_id: int,
        values: Mapping[str, object],
    ) -> ReportDefinition | None:
        """Update mutable report definition fields."""
        return self._report_definitions.update(report_definition_id, values)

    def update_report(
        self,
        report_definition_id: int,
        values: Mapping[str, object],
    ) -> ReportDefinition | None:
        """Update mutable report definition fields using a shorter alias."""
        return self.update_report_definition(report_definition_id, values)

    def delete_report_definition(self, report_definition_id: int) -> bool:
        """Soft-delete a report definition."""
        return self._report_definitions.delete(report_definition_id)

    def delete_report(self, report_definition_id: int) -> bool:
        """Soft-delete a report definition using a shorter alias."""
        return self.delete_report_definition(report_definition_id)

    def mark_report_definition_deleted(self, report_definition_id: int) -> bool:
        """Soft-delete a report definition using lifecycle alias."""
        return self._report_definitions.mark_deleted(report_definition_id)

    def report_definition_exists(
        self,
        report_definition_id: int,
        *,
        include_deleted: bool = False,
    ) -> bool:
        """Return whether a report definition exists."""
        return self._report_definitions.exists(
            report_definition_id,
            include_deleted=include_deleted,
        )

    def report_exists(
        self,
        report_definition_id: int,
        *,
        include_deleted: bool = False,
    ) -> bool:
        """Return whether a report definition exists using a shorter alias."""
        return self.report_definition_exists(
            report_definition_id,
            include_deleted=include_deleted,
        )

    # Report runs

    def create_report_run(self, report_run: ReportRun) -> ReportRun:
        """Create a report generation run."""
        return self._report_runs.create_run(report_run)

    def create_run(self, report_run: ReportRun) -> ReportRun:
        """Create a report generation run using a shorter alias."""
        return self.create_report_run(report_run)

    def get_report_run_by_id(self, run_id: int) -> ReportRun | None:
        """Return a report generation run by integer ID."""
        return self._report_runs.get_by_id(run_id)

    def get_run_by_id(self, run_id: int) -> ReportRun | None:
        """Return a report generation run by integer ID using a shorter alias."""
        return self.get_report_run_by_id(run_id)

    def get_report_run_by_uuid(self, run_uuid: UUID) -> ReportRun | None:
        """Return a report generation run by UUID."""
        return self._report_runs.get_by_uuid(run_uuid)

    def get_run_by_uuid(self, run_uuid: UUID) -> ReportRun | None:
        """Return a report generation run by UUID using a shorter alias."""
        return self.get_report_run_by_uuid(run_uuid)

    def list_report_runs(
        self,
        *,
        report_definition_id: int | None = None,
        requested_by_user_id: int | None = None,
        file_object_id: int | None = None,
        status: str | None = None,
        output_format: str | None = None,
        created_from: datetime | None = None,
        created_to: datetime | None = None,
        started_from: datetime | None = None,
        started_to: datetime | None = None,
        completed_from: datetime | None = None,
        completed_to: datetime | None = None,
        failed_from: datetime | None = None,
        failed_to: datetime | None = None,
        limit: int | None = None,
        offset: int | None = None,
    ) -> list[ReportRun]:
        """List report generation runs using repository filters."""
        return self._report_runs.list(
            report_definition_id=report_definition_id,
            requested_by_user_id=requested_by_user_id,
            file_object_id=file_object_id,
            status=status,
            output_format=output_format,
            created_from=created_from,
            created_to=created_to,
            started_from=started_from,
            started_to=started_to,
            completed_from=completed_from,
            completed_to=completed_to,
            failed_from=failed_from,
            failed_to=failed_to,
            limit=limit,
            offset=offset,
        )

    def list_runs(self, **filters: Any) -> list[ReportRun]:
        """List report generation runs using a shorter alias."""
        return self.list_report_runs(**filters)

    def count_report_runs(
        self,
        *,
        report_definition_id: int | None = None,
        requested_by_user_id: int | None = None,
        file_object_id: int | None = None,
        status: str | None = None,
        output_format: str | None = None,
        created_from: datetime | None = None,
        created_to: datetime | None = None,
        started_from: datetime | None = None,
        started_to: datetime | None = None,
        completed_from: datetime | None = None,
        completed_to: datetime | None = None,
        failed_from: datetime | None = None,
        failed_to: datetime | None = None,
    ) -> int:
        """Count report generation runs using repository filters."""
        return self._report_runs.count(
            report_definition_id=report_definition_id,
            requested_by_user_id=requested_by_user_id,
            file_object_id=file_object_id,
            status=status,
            output_format=output_format,
            created_from=created_from,
            created_to=created_to,
            started_from=started_from,
            started_to=started_to,
            completed_from=completed_from,
            completed_to=completed_to,
            failed_from=failed_from,
            failed_to=failed_to,
        )

    def count_runs(self, **filters: Any) -> int:
        """Count report generation runs using a shorter alias."""
        return self.count_report_runs(**filters)

    def update_report_run(
        self,
        run_id: int,
        values: Mapping[str, object],
    ) -> ReportRun | None:
        """Update mutable report generation run fields."""
        return self._report_runs.update(run_id, values)

    def update_run(
        self,
        run_id: int,
        values: Mapping[str, object],
    ) -> ReportRun | None:
        """Update mutable report generation run fields using a shorter alias."""
        return self.update_report_run(run_id, values)

    def mark_report_run_status(
        self,
        run_id: int,
        status: str,
        *,
        started_at: datetime | None = None,
        completed_at: datetime | None = None,
        failed_at: datetime | None = None,
        failure_reason: str | None = None,
        result_summary: Mapping[str, object] | None = None,
        row_count: int | None = None,
        file_object_id: int | None = None,
    ) -> ReportRun | None:
        """Update report generation run lifecycle status."""
        return self._report_runs.mark_status(
            run_id,
            status,
            started_at=started_at,
            completed_at=completed_at,
            failed_at=failed_at,
            failure_reason=failure_reason,
            result_summary=result_summary,
            row_count=row_count,
            file_object_id=file_object_id,
        )

    def mark_run_status(
        self,
        run_id: int,
        status: str,
        **values: Any,
    ) -> ReportRun | None:
        """Update report generation run lifecycle status using a shorter alias."""
        return self.mark_report_run_status(run_id, status, **values)

    def report_run_exists(self, run_id: int) -> bool:
        """Return whether a report generation run exists."""
        return self._report_runs.exists(run_id)

    def run_exists(self, run_id: int) -> bool:
        """Return whether a report generation run exists using a shorter alias."""
        return self.report_run_exists(run_id)

    # Analytics snapshots

    def create_analytics_snapshot(
        self,
        snapshot: AnalyticsSnapshot,
    ) -> AnalyticsSnapshot:
        """Create an analytics snapshot."""
        return self._analytics_snapshots.create_snapshot(snapshot)

    def create_snapshot(self, snapshot: AnalyticsSnapshot) -> AnalyticsSnapshot:
        """Create an analytics snapshot using a shorter alias."""
        return self.create_analytics_snapshot(snapshot)

    def get_analytics_snapshot_by_id(
        self,
        snapshot_id: int,
    ) -> AnalyticsSnapshot | None:
        """Return an analytics snapshot by integer ID."""
        return self._analytics_snapshots.get_by_id(snapshot_id)

    def get_snapshot_by_id(self, snapshot_id: int) -> AnalyticsSnapshot | None:
        """Return an analytics snapshot by integer ID using a shorter alias."""
        return self.get_analytics_snapshot_by_id(snapshot_id)

    def get_analytics_snapshot_by_uuid(
        self,
        snapshot_uuid: UUID,
    ) -> AnalyticsSnapshot | None:
        """Return an analytics snapshot by UUID."""
        return self._analytics_snapshots.get_by_uuid(snapshot_uuid)

    def get_snapshot_by_uuid(
        self,
        snapshot_uuid: UUID,
    ) -> AnalyticsSnapshot | None:
        """Return an analytics snapshot by UUID using a shorter alias."""
        return self.get_analytics_snapshot_by_uuid(snapshot_uuid)

    def list_analytics_snapshots(
        self,
        *,
        metric_key: str | None = None,
        source_module: str | None = None,
        entity_type: str | None = None,
        entity_id: str | None = None,
        period: str | None = None,
        status: str | None = None,
        period_start_from: datetime | None = None,
        period_start_to: datetime | None = None,
        period_end_from: datetime | None = None,
        period_end_to: datetime | None = None,
        calculated_from: datetime | None = None,
        calculated_to: datetime | None = None,
        limit: int | None = None,
        offset: int | None = None,
    ) -> list[AnalyticsSnapshot]:
        """List analytics snapshots using repository filters."""
        return self._analytics_snapshots.list(
            metric_key=metric_key,
            source_module=source_module,
            entity_type=entity_type,
            entity_id=entity_id,
            period=period,
            status=status,
            period_start_from=period_start_from,
            period_start_to=period_start_to,
            period_end_from=period_end_from,
            period_end_to=period_end_to,
            calculated_from=calculated_from,
            calculated_to=calculated_to,
            limit=limit,
            offset=offset,
        )

    def list_snapshots(self, **filters: Any) -> list[AnalyticsSnapshot]:
        """List analytics snapshots using a shorter alias."""
        return self.list_analytics_snapshots(**filters)

    def count_analytics_snapshots(
        self,
        *,
        metric_key: str | None = None,
        source_module: str | None = None,
        entity_type: str | None = None,
        entity_id: str | None = None,
        period: str | None = None,
        status: str | None = None,
        period_start_from: datetime | None = None,
        period_start_to: datetime | None = None,
        period_end_from: datetime | None = None,
        period_end_to: datetime | None = None,
        calculated_from: datetime | None = None,
        calculated_to: datetime | None = None,
    ) -> int:
        """Count analytics snapshots using repository filters."""
        return self._analytics_snapshots.count(
            metric_key=metric_key,
            source_module=source_module,
            entity_type=entity_type,
            entity_id=entity_id,
            period=period,
            status=status,
            period_start_from=period_start_from,
            period_start_to=period_start_to,
            period_end_from=period_end_from,
            period_end_to=period_end_to,
            calculated_from=calculated_from,
            calculated_to=calculated_to,
        )

    def count_snapshots(self, **filters: Any) -> int:
        """Count analytics snapshots using a shorter alias."""
        return self.count_analytics_snapshots(**filters)

    def update_analytics_snapshot(
        self,
        snapshot_id: int,
        values: Mapping[str, object],
    ) -> AnalyticsSnapshot | None:
        """Update mutable analytics snapshot fields."""
        return self._analytics_snapshots.update(snapshot_id, values)

    def update_snapshot(
        self,
        snapshot_id: int,
        values: Mapping[str, object],
    ) -> AnalyticsSnapshot | None:
        """Update mutable analytics snapshot fields using a shorter alias."""
        return self.update_analytics_snapshot(snapshot_id, values)

    def analytics_snapshot_exists(self, snapshot_id: int) -> bool:
        """Return whether an analytics snapshot exists."""
        exists = getattr(self._analytics_snapshots, "exists", None)
        if exists is not None:
            return bool(exists(snapshot_id))
        return self.get_analytics_snapshot_by_id(snapshot_id) is not None

    def snapshot_exists(self, snapshot_id: int) -> bool:
        """Return whether an analytics snapshot exists using a shorter alias."""
        return self.analytics_snapshot_exists(snapshot_id)

    @property
    def _dashboards(self) -> Any:
        return self._component_repository(
            "dashboards",
            "dashboard_definitions",
            "dashboard_repository",
            "dashboard_definition_repository",
        )

    @property
    def _report_definitions(self) -> Any:
        return self._component_repository(
            "report_definitions",
            "reports",
            "report_repository",
            "report_definition_repository",
        )

    @property
    def _report_runs(self) -> Any:
        return self._component_repository(
            "report_runs",
            "runs",
            "report_run_repository",
        )

    @property
    def _analytics_snapshots(self) -> Any:
        return self._component_repository(
            "analytics_snapshots",
            "snapshots",
            "analytics_snapshot_repository",
        )

    def _component_repository(self, *names: str) -> Any:
        for name in names:
            repository = getattr(self.repository, name, None)
            if repository is not None:
                return repository

        names_text = ", ".join(names)
        raise AttributeError(
            f"ReportingAnalyticsRepository does not expose any of: {names_text}"
        )
