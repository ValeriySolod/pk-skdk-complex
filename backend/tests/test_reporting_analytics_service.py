from __future__ import annotations

from datetime import datetime, timezone
from uuid import uuid4

import pytest
from sqlalchemy.orm import Session

from app.models import User
from app.modules.reporting_analytics.models import (
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
from app.modules.reporting_analytics.repository import ReportingAnalyticsRepository
from app.modules.reporting_analytics.service import ReportingAnalyticsService


@pytest.fixture()
def service(db_session: Session) -> ReportingAnalyticsService:
    return ReportingAnalyticsService(ReportingAnalyticsRepository(db_session))


def create_test_user(
    db_session: Session,
    username: str = "reporting-analytics-service-user",
) -> User:
    user = User(
        username=username,
        full_name="Reporting Analytics Service User",
        password_hash="not-used",
        role="test",
        is_active=True,
    )
    db_session.add(user)
    db_session.flush()
    return user


def create_dashboard(
    service: ReportingAnalyticsService,
    *,
    code: str = "operations-overview",
    name: str = "Operations overview",
    category: str | None = "operations",
    status: str = DashboardStatus.ACTIVE.value,
    owner_user_id: int | None = None,
    created_at: datetime | None = None,
) -> DashboardDefinition:
    return service.create_dashboard(
        DashboardDefinition(
            code=code,
            name=name,
            description="Operational metrics dashboard",
            category=category,
            status=status,
            owner_user_id=owner_user_id,
            layout_config={"columns": 12},
            widget_config={"widgets": ["documents", "notifications"]},
            filter_config={"period": "30d"},
            created_at=created_at,
        ),
    )


def create_report(
    service: ReportingAnalyticsService,
    *,
    code: str = "documents-summary",
    name: str = "Documents summary",
    category: str | None = "documents",
    source_module: str | None = "document_management",
    status: str = ReportDefinitionStatus.ACTIVE.value,
    default_format: str = ReportOutputFormat.PDF.value,
    owner_user_id: int | None = None,
    created_at: datetime | None = None,
) -> ReportDefinition:
    return service.create_report(
        ReportDefinition(
            code=code,
            name=name,
            description="Document workflow summary",
            category=category,
            source_module=source_module,
            status=status,
            default_format=default_format,
            owner_user_id=owner_user_id,
            query_config={"select": ["id"]},
            filter_schema={"properties": {"date_from": {"type": "string"}}},
            layout_config={"template": "table"},
            created_at=created_at,
        ),
    )


def create_run(
    service: ReportingAnalyticsService,
    *,
    report_definition_id: int,
    requested_by_user_id: int | None = None,
    status: str = ReportRunStatus.QUEUED.value,
    output_format: str = ReportOutputFormat.PDF.value,
    created_at: datetime | None = None,
) -> ReportRun:
    return service.create_run(
        ReportRun(
            report_definition_id=report_definition_id,
            requested_by_user_id=requested_by_user_id,
            status=status,
            output_format=output_format,
            parameters={"period": "month"},
            created_at=created_at,
        ),
    )


def create_snapshot(
    service: ReportingAnalyticsService,
    *,
    metric_key: str = "documents.total",
    source_module: str | None = "document_management",
    entity_type: str | None = "organization",
    entity_id: str | None = "ORG-001",
    period: str = AnalyticsSnapshotPeriod.DAILY.value,
    status: str = AnalyticsSnapshotStatus.READY.value,
    calculated_at: datetime | None = None,
) -> AnalyticsSnapshot:
    return service.create_snapshot(
        AnalyticsSnapshot(
            metric_key=metric_key,
            metric_name="Total documents",
            source_module=source_module,
            entity_type=entity_type,
            entity_id=entity_id,
            period=period,
            status=status,
            value={"count": 10},
            dimensions={"department": "safety"},
            calculated_at=calculated_at,
        ),
    )


def test_reporting_analytics_service_health_and_dashboard_lifecycle(
    service: ReportingAnalyticsService,
    db_session: Session,
) -> None:
    owner = create_test_user(db_session)
    dashboard = create_dashboard(service, owner_user_id=owner.id)
    original_uuid = dashboard.dashboard_uuid

    assert service.health() == {"status": "healthy", "module": "reporting_analytics"}
    assert dashboard.id is not None
    assert service.get_dashboard_by_id(dashboard.id) == dashboard
    assert service.get_dashboard_by_uuid(original_uuid) == dashboard
    assert service.get_dashboard_by_code(dashboard.code) == dashboard
    assert service.dashboard_exists(dashboard.id) is True
    assert service.get_dashboard_by_id(999) is None
    assert service.get_dashboard_by_uuid(uuid4()) is None
    assert service.dashboard_exists(999) is False

    updated = service.update_dashboard(
        dashboard.id,
        {
            "name": "Updated operations overview",
            "status": DashboardStatus.ARCHIVED.value,
            "layout_config": {"columns": 6},
        },
    )

    assert updated is dashboard
    assert dashboard.dashboard_uuid == original_uuid
    assert dashboard.name == "Updated operations overview"
    assert dashboard.status == DashboardStatus.ARCHIVED.value
    assert dashboard.layout_config == {"columns": 6}
    assert service.update_dashboard(999, {"name": "Missing"}) is None
    with pytest.raises(ValueError, match="Unsupported dashboard update fields: id"):
        service.update_dashboard(dashboard.id, {"id": 999})

    assert service.mark_dashboard_deleted(dashboard.id) is True
    assert dashboard.deleted_at is not None
    assert service.get_dashboard_by_id(dashboard.id) is None
    assert service.get_dashboard_by_id(dashboard.id, include_deleted=True) == dashboard
    assert service.dashboard_exists(dashboard.id) is False
    assert service.dashboard_exists(dashboard.id, include_deleted=True) is True
    assert service.delete_dashboard(999) is False


def test_reporting_analytics_service_report_definition_aliases_filters_and_soft_delete(
    service: ReportingAnalyticsService,
    db_session: Session,
) -> None:
    owner = create_test_user(db_session, "reporting-service-report-owner")
    first = create_report(
        service,
        code="documents-first",
        owner_user_id=owner.id,
        created_at=datetime(2026, 7, 5, 9, 0, 0),
    )
    second = create_report(
        service,
        code="audit-second",
        category="audit",
        source_module="audit_log",
        default_format=ReportOutputFormat.CSV.value,
        owner_user_id=owner.id,
        created_at=datetime(2026, 7, 5, 10, 0, 0),
    )
    original_uuid = first.report_uuid

    assert service.get_report_definition_by_id(first.id) == first
    assert service.get_report_by_id(first.id) == first
    assert service.get_report_definition_by_uuid(original_uuid) == first
    assert service.get_report_by_uuid(original_uuid) == first
    assert service.get_report_definition_by_code(first.code) == first
    assert service.get_report_by_code(first.code) == first
    assert service.report_definition_exists(first.id) is True
    assert service.report_exists(first.id) is True
    assert service.list_report_definitions() == [second, first]
    assert service.list_reports(source_module="audit_log") == [second]
    assert service.count_report_definitions(owner_user_id=owner.id) == 2
    assert service.count_reports(default_format=ReportOutputFormat.CSV.value) == 1

    updated = service.update_report(
        first.id,
        {
            "default_format": ReportOutputFormat.XLSX.value,
            "last_generated_at": datetime.now(timezone.utc),
        },
    )

    assert updated is first
    assert first.report_uuid == original_uuid
    assert first.default_format == ReportOutputFormat.XLSX.value
    assert service.mark_report_definition_deleted(first.id) is True
    assert service.get_report_by_id(first.id) is None
    assert service.get_report_by_id(first.id, include_deleted=True) == first
    assert service.count_reports() == 1
    assert service.count_reports(include_deleted=True) == 2
    assert service.delete_report(999) is False


def test_reporting_analytics_service_report_run_lifecycle_and_relationship_filters(
    service: ReportingAnalyticsService,
    db_session: Session,
) -> None:
    requester = create_test_user(db_session, "reporting-service-run-requester")
    report = create_report(service, owner_user_id=requester.id)
    other_report = create_report(
        service,
        code="notifications-summary",
        source_module="notifications",
    )
    first = create_run(
        service,
        report_definition_id=report.id,
        requested_by_user_id=requester.id,
        created_at=datetime(2026, 7, 5, 9, 0, 0),
    )
    second = create_run(
        service,
        report_definition_id=other_report.id,
        status=ReportRunStatus.FAILED.value,
        output_format=ReportOutputFormat.CSV.value,
        created_at=datetime(2026, 7, 5, 10, 0, 0),
    )
    original_uuid = first.run_uuid

    assert service.get_report_run_by_id(first.id) == first
    assert service.get_run_by_id(first.id) == first
    assert service.get_report_run_by_uuid(original_uuid) == first
    assert service.get_run_by_uuid(original_uuid) == first
    assert service.report_run_exists(first.id) is True
    assert service.run_exists(first.id) is True
    assert service.list_report_runs() == [second, first]
    assert service.list_runs(report_definition_id=report.id) == [first]
    assert service.count_report_runs(requested_by_user_id=requester.id) == 1
    assert service.count_runs(status=ReportRunStatus.FAILED.value) == 1

    completed_at = datetime.now(timezone.utc)
    updated = service.mark_run_status(
        first.id,
        ReportRunStatus.COMPLETED.value,
        completed_at=completed_at,
        result_summary={"rows": 25},
        row_count=25,
    )

    assert updated is first
    assert first.run_uuid == original_uuid
    assert first.status == ReportRunStatus.COMPLETED.value
    assert first.completed_at == completed_at
    assert first.result_summary == {"rows": 25}
    assert first.row_count == 25
    assert service.update_run(999, {"status": ReportRunStatus.CANCELLED.value}) is None
    with pytest.raises(ValueError, match="Unsupported report run update fields: id"):
        service.update_report_run(first.id, {"id": 999})


def test_reporting_analytics_service_analytics_snapshot_aliases_filters_and_update(
    service: ReportingAnalyticsService,
) -> None:
    first = create_snapshot(
        service,
        calculated_at=datetime(2026, 7, 5, 9, 0, 0),
    )
    second = create_snapshot(
        service,
        metric_key="notifications.sent",
        source_module="notifications",
        entity_type="user",
        entity_id="42",
        period=AnalyticsSnapshotPeriod.MONTHLY.value,
        status=AnalyticsSnapshotStatus.STALE.value,
        calculated_at=datetime(2026, 7, 5, 10, 0, 0),
    )
    original_uuid = first.snapshot_uuid

    assert service.get_analytics_snapshot_by_id(first.id) == first
    assert service.get_snapshot_by_id(first.id) == first
    assert service.get_analytics_snapshot_by_uuid(original_uuid) == first
    assert service.get_snapshot_by_uuid(original_uuid) == first
    assert service.analytics_snapshot_exists(first.id) is True
    assert service.snapshot_exists(first.id) is True
    assert service.get_snapshot_by_uuid(uuid4()) is None
    assert service.list_analytics_snapshots() == [second, first]
    assert service.list_snapshots(source_module="notifications") == [second]
    assert (
        service.count_analytics_snapshots(period=AnalyticsSnapshotPeriod.DAILY.value) == 1
    )
    assert service.count_snapshots(status=AnalyticsSnapshotStatus.STALE.value) == 1

    updated = service.update_snapshot(
        first.id,
        {
            "status": AnalyticsSnapshotStatus.FAILED.value,
            "value": {"count": 0},
            "failure_reason": "Source unavailable",
        },
    )

    assert updated is first
    assert first.snapshot_uuid == original_uuid
    assert first.status == AnalyticsSnapshotStatus.FAILED.value
    assert first.value == {"count": 0}
    assert first.failure_reason == "Source unavailable"
    assert (
        service.update_analytics_snapshot(
            999,
            {"status": AnalyticsSnapshotStatus.READY.value},
        )
        is None
    )
    with pytest.raises(
        ValueError,
        match="Unsupported analytics snapshot update fields: id",
    ):
        service.update_snapshot(first.id, {"id": 999})
