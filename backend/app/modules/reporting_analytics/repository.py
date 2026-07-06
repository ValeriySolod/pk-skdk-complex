"""Repository operations for the Reporting & Analytics module."""

from __future__ import annotations

from collections.abc import Mapping
from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import Select, func, select
from sqlalchemy.orm import Session

from app.modules.reporting_analytics.models import (
    AnalyticsSnapshot,
    DashboardDefinition,
    ReportDefinition,
    ReportRun,
)


class DashboardDefinitionRepository:
    """Persistence operations for dashboard definitions."""

    _mutable_fields = frozenset(
        {
            "code",
            "name",
            "description",
            "category",
            "status",
            "owner_user_id",
            "layout_config",
            "widget_config",
            "filter_config",
        },
    )

    def __init__(self, db: Session) -> None:
        self.db = db

    def create(self, dashboard: DashboardDefinition) -> DashboardDefinition:
        self.db.add(dashboard)
        self.db.flush()
        return dashboard

    def create_dashboard(self, dashboard: DashboardDefinition) -> DashboardDefinition:
        return self.create(dashboard)

    def get_by_id(
        self,
        dashboard_id: int,
        *,
        include_deleted: bool = False,
    ) -> DashboardDefinition | None:
        dashboard = self.db.get(DashboardDefinition, dashboard_id)
        if (
            dashboard is not None
            and dashboard.deleted_at is not None
            and not include_deleted
        ):
            return None
        return dashboard

    def get_by_uuid(
        self,
        dashboard_uuid: UUID,
        *,
        include_deleted: bool = False,
    ) -> DashboardDefinition | None:
        query = select(DashboardDefinition).where(
            DashboardDefinition.dashboard_uuid == dashboard_uuid,
        )
        if not include_deleted:
            query = query.where(DashboardDefinition.deleted_at.is_(None))
        return self.db.scalar(query)

    def get_by_code(
        self,
        code: str,
        *,
        include_deleted: bool = False,
    ) -> DashboardDefinition | None:
        query = select(DashboardDefinition).where(DashboardDefinition.code == code)
        if not include_deleted:
            query = query.where(DashboardDefinition.deleted_at.is_(None))
        return self.db.scalar(query)

    def list(
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
        query = self._build_query(
            category=category,
            status=status,
            owner_user_id=owner_user_id,
            created_from=created_from,
            created_to=created_to,
            include_deleted=include_deleted,
        ).order_by(DashboardDefinition.created_at.desc(), DashboardDefinition.id.desc())

        if offset is not None:
            query = query.offset(offset)
        if limit is not None:
            query = query.limit(limit)

        return list(self.db.scalars(query).all())

    def count(
        self,
        *,
        category: str | None = None,
        status: str | None = None,
        owner_user_id: int | None = None,
        created_from: datetime | None = None,
        created_to: datetime | None = None,
        include_deleted: bool = False,
    ) -> int:
        query = self._build_query(
            category=category,
            status=status,
            owner_user_id=owner_user_id,
            created_from=created_from,
            created_to=created_to,
            include_deleted=include_deleted,
        )
        return self.db.scalar(select(func.count()).select_from(query.subquery())) or 0

    def update(
        self,
        dashboard_id: int,
        values: Mapping[str, object],
    ) -> DashboardDefinition | None:
        dashboard = self.get_by_id(dashboard_id)
        if dashboard is None:
            return None

        unsupported_fields = set(values) - self._mutable_fields
        if unsupported_fields:
            fields = ", ".join(sorted(unsupported_fields))
            raise ValueError(f"Unsupported dashboard update fields: {fields}")

        for field, value in values.items():
            setattr(dashboard, field, value)

        self.db.flush()
        return dashboard

    def delete(self, dashboard_id: int) -> bool:
        dashboard = self.get_by_id(dashboard_id)
        if dashboard is None:
            return False

        dashboard.deleted_at = datetime.now(timezone.utc)
        self.db.flush()
        return True

    def mark_deleted(self, dashboard_id: int) -> bool:
        return self.delete(dashboard_id)

    def exists(self, dashboard_id: int, *, include_deleted: bool = False) -> bool:
        return (
            self.get_by_id(
                dashboard_id,
                include_deleted=include_deleted,
            )
            is not None
        )

    def health(self) -> bool:
        return self.db.scalar(select(1)) == 1

    def _build_query(
        self,
        *,
        category: str | None = None,
        status: str | None = None,
        owner_user_id: int | None = None,
        created_from: datetime | None = None,
        created_to: datetime | None = None,
        include_deleted: bool = False,
    ) -> Select[tuple[DashboardDefinition]]:
        query = select(DashboardDefinition)

        if not include_deleted:
            query = query.where(DashboardDefinition.deleted_at.is_(None))
        if category is not None:
            query = query.where(DashboardDefinition.category == category)
        if status is not None:
            query = query.where(DashboardDefinition.status == status)
        if owner_user_id is not None:
            query = query.where(DashboardDefinition.owner_user_id == owner_user_id)
        if created_from is not None:
            query = query.where(DashboardDefinition.created_at >= created_from)
        if created_to is not None:
            query = query.where(DashboardDefinition.created_at <= created_to)

        return query


class ReportDefinitionRepository:
    """Persistence operations for report definitions."""

    _mutable_fields = frozenset(
        {
            "code",
            "name",
            "description",
            "category",
            "source_module",
            "status",
            "default_format",
            "owner_user_id",
            "query_config",
            "filter_schema",
            "layout_config",
            "last_generated_at",
        },
    )

    def __init__(self, db: Session) -> None:
        self.db = db

    def create(self, report: ReportDefinition) -> ReportDefinition:
        self.db.add(report)
        self.db.flush()
        return report

    def create_report_definition(self, report: ReportDefinition) -> ReportDefinition:
        return self.create(report)

    def get_by_id(
        self,
        report_definition_id: int,
        *,
        include_deleted: bool = False,
    ) -> ReportDefinition | None:
        report = self.db.get(ReportDefinition, report_definition_id)
        if report is not None and report.deleted_at is not None and not include_deleted:
            return None
        return report

    def get_by_uuid(
        self,
        report_uuid: UUID,
        *,
        include_deleted: bool = False,
    ) -> ReportDefinition | None:
        query = select(ReportDefinition).where(
            ReportDefinition.report_uuid == report_uuid,
        )
        if not include_deleted:
            query = query.where(ReportDefinition.deleted_at.is_(None))
        return self.db.scalar(query)

    def get_by_code(
        self,
        code: str,
        *,
        include_deleted: bool = False,
    ) -> ReportDefinition | None:
        query = select(ReportDefinition).where(ReportDefinition.code == code)
        if not include_deleted:
            query = query.where(ReportDefinition.deleted_at.is_(None))
        return self.db.scalar(query)

    def list(
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
        query = self._build_query(
            category=category,
            source_module=source_module,
            status=status,
            default_format=default_format,
            owner_user_id=owner_user_id,
            created_from=created_from,
            created_to=created_to,
            include_deleted=include_deleted,
        ).order_by(ReportDefinition.created_at.desc(), ReportDefinition.id.desc())

        if offset is not None:
            query = query.offset(offset)
        if limit is not None:
            query = query.limit(limit)

        return list(self.db.scalars(query).all())

    def count(
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
        query = self._build_query(
            category=category,
            source_module=source_module,
            status=status,
            default_format=default_format,
            owner_user_id=owner_user_id,
            created_from=created_from,
            created_to=created_to,
            include_deleted=include_deleted,
        )
        return self.db.scalar(select(func.count()).select_from(query.subquery())) or 0

    def update(
        self,
        report_definition_id: int,
        values: Mapping[str, object],
    ) -> ReportDefinition | None:
        report = self.get_by_id(report_definition_id)
        if report is None:
            return None

        unsupported_fields = set(values) - self._mutable_fields
        if unsupported_fields:
            fields = ", ".join(sorted(unsupported_fields))
            raise ValueError(f"Unsupported report definition update fields: {fields}")

        for field, value in values.items():
            setattr(report, field, value)

        self.db.flush()
        return report

    def delete(self, report_definition_id: int) -> bool:
        report = self.get_by_id(report_definition_id)
        if report is None:
            return False

        report.deleted_at = datetime.now(timezone.utc)
        self.db.flush()
        return True

    def mark_deleted(self, report_definition_id: int) -> bool:
        return self.delete(report_definition_id)

    def exists(
        self,
        report_definition_id: int,
        *,
        include_deleted: bool = False,
    ) -> bool:
        return (
            self.get_by_id(
                report_definition_id,
                include_deleted=include_deleted,
            )
            is not None
        )

    def health(self) -> bool:
        return self.db.scalar(select(1)) == 1

    def _build_query(
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
    ) -> Select[tuple[ReportDefinition]]:
        query = select(ReportDefinition)

        if not include_deleted:
            query = query.where(ReportDefinition.deleted_at.is_(None))
        if category is not None:
            query = query.where(ReportDefinition.category == category)
        if source_module is not None:
            query = query.where(ReportDefinition.source_module == source_module)
        if status is not None:
            query = query.where(ReportDefinition.status == status)
        if default_format is not None:
            query = query.where(ReportDefinition.default_format == default_format)
        if owner_user_id is not None:
            query = query.where(ReportDefinition.owner_user_id == owner_user_id)
        if created_from is not None:
            query = query.where(ReportDefinition.created_at >= created_from)
        if created_to is not None:
            query = query.where(ReportDefinition.created_at <= created_to)

        return query


class ReportRunRepository:
    """Persistence operations for report generation runs."""

    _mutable_fields = frozenset(
        {
            "requested_by_user_id",
            "file_object_id",
            "status",
            "output_format",
            "parameters",
            "result_summary",
            "row_count",
            "started_at",
            "completed_at",
            "failed_at",
            "failure_reason",
        },
    )

    def __init__(self, db: Session) -> None:
        self.db = db

    def create(self, report_run: ReportRun) -> ReportRun:
        self.db.add(report_run)
        self.db.flush()
        return report_run

    def create_run(self, report_run: ReportRun) -> ReportRun:
        return self.create(report_run)

    def get_by_id(self, run_id: int) -> ReportRun | None:
        return self.db.get(ReportRun, run_id)

    def get_by_uuid(self, run_uuid: UUID) -> ReportRun | None:
        return self.db.scalar(
            select(ReportRun).where(ReportRun.run_uuid == run_uuid),
        )

    def list(
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
        query = self._build_query(
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
        ).order_by(ReportRun.created_at.desc(), ReportRun.id.desc())

        if offset is not None:
            query = query.offset(offset)
        if limit is not None:
            query = query.limit(limit)

        return list(self.db.scalars(query).all())

    def count(
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
        query = self._build_query(
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
        return self.db.scalar(select(func.count()).select_from(query.subquery())) or 0

    def update(
        self,
        run_id: int,
        values: Mapping[str, object],
    ) -> ReportRun | None:
        report_run = self.get_by_id(run_id)
        if report_run is None:
            return None

        unsupported_fields = set(values) - self._mutable_fields
        if unsupported_fields:
            fields = ", ".join(sorted(unsupported_fields))
            raise ValueError(f"Unsupported report run update fields: {fields}")

        for field, value in values.items():
            setattr(report_run, field, value)

        self.db.flush()
        return report_run

    def mark_status(
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
        values: dict[str, object] = {"status": status}

        if started_at is not None:
            values["started_at"] = started_at
        if completed_at is not None:
            values["completed_at"] = completed_at
        if failed_at is not None:
            values["failed_at"] = failed_at
        if failure_reason is not None:
            values["failure_reason"] = failure_reason
        if result_summary is not None:
            values["result_summary"] = dict(result_summary)
        if row_count is not None:
            values["row_count"] = row_count
        if file_object_id is not None:
            values["file_object_id"] = file_object_id

        return self.update(run_id, values)

    def exists(self, run_id: int) -> bool:
        return self.get_by_id(run_id) is not None

    def health(self) -> bool:
        return self.db.scalar(select(1)) == 1

    def _build_query(
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
    ) -> Select[tuple[ReportRun]]:
        query = select(ReportRun)

        if report_definition_id is not None:
            query = query.where(ReportRun.report_definition_id == report_definition_id)
        if requested_by_user_id is not None:
            query = query.where(ReportRun.requested_by_user_id == requested_by_user_id)
        if file_object_id is not None:
            query = query.where(ReportRun.file_object_id == file_object_id)
        if status is not None:
            query = query.where(ReportRun.status == status)
        if output_format is not None:
            query = query.where(ReportRun.output_format == output_format)
        if created_from is not None:
            query = query.where(ReportRun.created_at >= created_from)
        if created_to is not None:
            query = query.where(ReportRun.created_at <= created_to)
        if started_from is not None:
            query = query.where(ReportRun.started_at >= started_from)
        if started_to is not None:
            query = query.where(ReportRun.started_at <= started_to)
        if completed_from is not None:
            query = query.where(ReportRun.completed_at >= completed_from)
        if completed_to is not None:
            query = query.where(ReportRun.completed_at <= completed_to)
        if failed_from is not None:
            query = query.where(ReportRun.failed_at >= failed_from)
        if failed_to is not None:
            query = query.where(ReportRun.failed_at <= failed_to)

        return query


class AnalyticsSnapshotRepository:
    """Persistence operations for analytics snapshots."""

    _mutable_fields = frozenset(
        {
            "metric_key",
            "metric_name",
            "source_module",
            "entity_type",
            "entity_id",
            "period",
            "status",
            "value",
            "dimensions",
            "period_start",
            "period_end",
            "calculated_at",
            "failure_reason",
        },
    )

    def __init__(self, db: Session) -> None:
        self.db = db

    def create(self, snapshot: AnalyticsSnapshot) -> AnalyticsSnapshot:
        self.db.add(snapshot)
        self.db.flush()
        return snapshot

    def create_snapshot(self, snapshot: AnalyticsSnapshot) -> AnalyticsSnapshot:
        return self.create(snapshot)

    def get_by_id(self, snapshot_id: int) -> AnalyticsSnapshot | None:
        return self.db.get(AnalyticsSnapshot, snapshot_id)

    def get_by_uuid(self, snapshot_uuid: UUID) -> AnalyticsSnapshot | None:
        return self.db.scalar(
            select(AnalyticsSnapshot).where(
                AnalyticsSnapshot.snapshot_uuid == snapshot_uuid,
            ),
        )

    def list(
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
        query = self._build_query(
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
        ).order_by(AnalyticsSnapshot.calculated_at.desc(), AnalyticsSnapshot.id.desc())

        if offset is not None:
            query = query.offset(offset)
        if limit is not None:
            query = query.limit(limit)

        return list(self.db.scalars(query).all())

    def count(
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
        query = self._build_query(
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
        return self.db.scalar(select(func.count()).select_from(query.subquery())) or 0

    def update(
        self,
        snapshot_id: int,
        values: Mapping[str, object],
    ) -> AnalyticsSnapshot | None:
        snapshot = self.get_by_id(snapshot_id)
        if snapshot is None:
            return None

        unsupported_fields = set(values) - self._mutable_fields
        if unsupported_fields:
            fields = ", ".join(sorted(unsupported_fields))
            raise ValueError(f"Unsupported analytics snapshot update fields: {fields}")

        for field, value in values.items():
            setattr(snapshot, field, value)

        self.db.flush()
        return snapshot

    def exists(self, snapshot_id: int) -> bool:
        return self.get_by_id(snapshot_id) is not None

    def health(self) -> bool:
        return self.db.scalar(select(1)) == 1

    def _build_query(
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
    ) -> Select[tuple[AnalyticsSnapshot]]:
        query = select(AnalyticsSnapshot)

        if metric_key is not None:
            query = query.where(AnalyticsSnapshot.metric_key == metric_key)
        if source_module is not None:
            query = query.where(AnalyticsSnapshot.source_module == source_module)
        if entity_type is not None:
            query = query.where(AnalyticsSnapshot.entity_type == entity_type)
        if entity_id is not None:
            query = query.where(AnalyticsSnapshot.entity_id == entity_id)
        if period is not None:
            query = query.where(AnalyticsSnapshot.period == period)
        if status is not None:
            query = query.where(AnalyticsSnapshot.status == status)
        if period_start_from is not None:
            query = query.where(AnalyticsSnapshot.period_start >= period_start_from)
        if period_start_to is not None:
            query = query.where(AnalyticsSnapshot.period_start <= period_start_to)
        if period_end_from is not None:
            query = query.where(AnalyticsSnapshot.period_end >= period_end_from)
        if period_end_to is not None:
            query = query.where(AnalyticsSnapshot.period_end <= period_end_to)
        if calculated_from is not None:
            query = query.where(AnalyticsSnapshot.calculated_at >= calculated_from)
        if calculated_to is not None:
            query = query.where(AnalyticsSnapshot.calculated_at <= calculated_to)

        return query


class ReportingAnalyticsRepository:
    """Persistence boundary for reporting and analytics data."""

    def __init__(self, db: Session) -> None:
        self.db = db
        self.dashboards = DashboardDefinitionRepository(db)
        self.report_definitions = ReportDefinitionRepository(db)
        self.report_runs = ReportRunRepository(db)
        self.snapshots = AnalyticsSnapshotRepository(db)

    def health(self) -> bool:
        return (
            self.dashboards.health()
            and self.report_definitions.health()
            and self.report_runs.health()
            and self.snapshots.health()
        )


__all__ = [
    "AnalyticsSnapshotRepository",
    "DashboardDefinitionRepository",
    "ReportDefinitionRepository",
    "ReportRunRepository",
    "ReportingAnalyticsRepository",
]
