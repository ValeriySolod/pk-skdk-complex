from __future__ import annotations

from datetime import datetime
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
from app.modules.reporting_analytics.repository import (
    AnalyticsSnapshotRepository,
    DashboardDefinitionRepository,
    ReportDefinitionRepository,
    ReportingAnalyticsRepository,
    ReportRunRepository,
)


def create_test_user(
    db_session: Session,
    username: str = "reporting-analytics-repository-user",
) -> User:
    user = User(
        username=username,
        full_name="Reporting Analytics Repository User",
        password_hash="not-used",
        role="test",
        is_active=True,
    )
    db_session.add(user)
    db_session.flush()
    return user


def create_dashboard(
    repository: DashboardDefinitionRepository,
    *,
    code: str = "operations-overview",
    name: str = "Operations overview",
    description: str | None = "Operational metrics dashboard",
    category: str | None = "operations",
    status: str = DashboardStatus.ACTIVE.value,
    owner_user_id: int | None = None,
    layout_config: dict[str, object] | None = None,
    widget_config: dict[str, object] | None = None,
    filter_config: dict[str, object] | None = None,
    created_at: datetime | None = None,
) -> DashboardDefinition:
    return repository.create(
        DashboardDefinition(
            code=code,
            name=name,
            description=description,
            category=category,
            status=status,
            owner_user_id=owner_user_id,
            layout_config=layout_config if layout_config is not None else {"columns": 12},
            widget_config=widget_config
            if widget_config is not None
            else {"widgets": ["documents", "notifications"]},
            filter_config=filter_config if filter_config is not None else {"period": "30d"},
            created_at=created_at,
        ),
    )


def create_report_definition(
    repository: ReportDefinitionRepository,
    *,
    code: str = "documents-summary",
    name: str = "Documents summary",
    description: str | None = "Document workflow summary",
    category: str | None = "documents",
    source_module: str | None = "document_management",
    status: str = ReportDefinitionStatus.ACTIVE.value,
    default_format: str = ReportOutputFormat.PDF.value,
    owner_user_id: int | None = None,
    query_config: dict[str, object] | None = None,
    filter_schema: dict[str, object] | None = None,
    layout_config: dict[str, object] | None = None,
    last_generated_at: datetime | None = None,
    created_at: datetime | None = None,
) -> ReportDefinition:
    return repository.create(
        ReportDefinition(
            code=code,
            name=name,
            description=description,
            category=category,
            source_module=source_module,
            status=status,
            default_format=default_format,
            owner_user_id=owner_user_id,
            query_config=query_config if query_config is not None else {"select": ["id"]},
            filter_schema=filter_schema
            if filter_schema is not None
            else {"properties": {"date_from": {"type": "string"}}},
            layout_config=layout_config if layout_config is not None else {"template": "table"},
            last_generated_at=last_generated_at,
            created_at=created_at,
        ),
    )


def create_report_run(
    repository: ReportRunRepository,
    *,
    report_definition_id: int,
    requested_by_user_id: int | None = None,
    file_object_id: int | None = None,
    status: str = ReportRunStatus.QUEUED.value,
    output_format: str = ReportOutputFormat.PDF.value,
    parameters: dict[str, object] | None = None,
    result_summary: dict[str, object] | None = None,
    row_count: int = 0,
    started_at: datetime | None = None,
    completed_at: datetime | None = None,
    failed_at: datetime | None = None,
    failure_reason: str | None = None,
    created_at: datetime | None = None,
) -> ReportRun:
    return repository.create(
        ReportRun(
            report_definition_id=report_definition_id,
            requested_by_user_id=requested_by_user_id,
            file_object_id=file_object_id,
            status=status,
            output_format=output_format,
            parameters=parameters if parameters is not None else {"period": "month"},
            result_summary=result_summary,
            row_count=row_count,
            started_at=started_at,
            completed_at=completed_at,
            failed_at=failed_at,
            failure_reason=failure_reason,
            created_at=created_at,
        ),
    )


def create_snapshot(
    repository: AnalyticsSnapshotRepository,
    *,
    metric_key: str = "documents.total",
    metric_name: str = "Total documents",
    source_module: str | None = "document_management",
    entity_type: str | None = "organization",
    entity_id: str | None = "ORG-001",
    period: str = AnalyticsSnapshotPeriod.DAILY.value,
    status: str = AnalyticsSnapshotStatus.READY.value,
    value: dict[str, object] | None = None,
    dimensions: dict[str, object] | None = None,
    period_start: datetime | None = None,
    period_end: datetime | None = None,
    calculated_at: datetime | None = None,
    failure_reason: str | None = None,
    created_at: datetime | None = None,
) -> AnalyticsSnapshot:
    return repository.create(
        AnalyticsSnapshot(
            metric_key=metric_key,
            metric_name=metric_name,
            source_module=source_module,
            entity_type=entity_type,
            entity_id=entity_id,
            period=period,
            status=status,
            value=value if value is not None else {"count": 10},
            dimensions=dimensions if dimensions is not None else {"department": "safety"},
            period_start=period_start,
            period_end=period_end,
            calculated_at=calculated_at,
            failure_reason=failure_reason,
            created_at=created_at,
        ),
    )


def test_dashboard_repository_create_lookup_update_soft_delete_and_health(
    db_session: Session,
) -> None:
    repository = DashboardDefinitionRepository(db_session)
    owner = create_test_user(db_session)

    dashboard = create_dashboard(repository, owner_user_id=owner.id)
    alias_dashboard = repository.create_dashboard(
        DashboardDefinition(code="alias-dashboard", name="Alias dashboard"),
    )
    original_uuid = dashboard.dashboard_uuid

    assert repository.health() is True
    assert dashboard.id is not None
    assert dashboard.dashboard_uuid is not None
    assert alias_dashboard.id is not None
    assert repository.get_by_id(dashboard.id) == dashboard
    assert repository.get_by_uuid(original_uuid) == dashboard
    assert repository.get_by_code(dashboard.code) == dashboard
    assert repository.exists(dashboard.id) is True
    assert repository.get_by_id(999) is None
    assert repository.get_by_uuid(uuid4()) is None
    assert repository.get_by_code("missing") is None
    assert repository.exists(999) is False

    updated_dashboard = repository.update(
        dashboard.id,
        {
            "name": "Updated operations overview",
            "status": DashboardStatus.ARCHIVED.value,
            "layout_config": {"columns": 6},
            "widget_config": {"widgets": ["reports"]},
            "filter_config": {"period": "7d"},
        },
    )

    assert updated_dashboard is dashboard
    assert dashboard.dashboard_uuid == original_uuid
    assert dashboard.name == "Updated operations overview"
    assert dashboard.status == DashboardStatus.ARCHIVED.value
    assert dashboard.layout_config == {"columns": 6}
    assert repository.update(999, {"name": "Missing"}) is None
    with pytest.raises(ValueError, match="Unsupported dashboard update fields: id"):
        repository.update(dashboard.id, {"id": 999})

    assert repository.mark_deleted(dashboard.id) is True
    assert dashboard.deleted_at is not None
    assert repository.get_by_id(dashboard.id) is None
    assert repository.get_by_id(dashboard.id, include_deleted=True) == dashboard
    assert repository.get_by_uuid(original_uuid) is None
    assert repository.get_by_uuid(original_uuid, include_deleted=True) == dashboard
    assert repository.exists(dashboard.id) is False
    assert repository.exists(dashboard.id, include_deleted=True) is True
    assert repository.list() == [alias_dashboard]
    assert repository.count() == 1
    assert repository.list(include_deleted=True) == [alias_dashboard, dashboard]
    assert repository.count(include_deleted=True) == 2
    assert repository.delete(999) is False


def test_dashboard_repository_list_filters_count_ordering_and_pagination(
    db_session: Session,
) -> None:
    repository = DashboardDefinitionRepository(db_session)
    owner = create_test_user(db_session, "dashboard-filter-owner")
    other_owner = create_test_user(db_session, "dashboard-filter-other")

    first = create_dashboard(
        repository,
        code="operations-first",
        category="operations",
        owner_user_id=owner.id,
        created_at=datetime(2026, 7, 5, 9, 0, 0),
    )
    second = create_dashboard(
        repository,
        code="safety-second",
        name="Safety dashboard",
        category="safety",
        status=DashboardStatus.DRAFT.value,
        owner_user_id=owner.id,
        created_at=datetime(2026, 7, 5, 10, 0, 0),
    )
    third = create_dashboard(
        repository,
        code="quality-third",
        name="Quality dashboard",
        category="quality",
        owner_user_id=other_owner.id,
        created_at=datetime(2026, 7, 5, 11, 0, 0),
    )

    assert repository.list() == [third, second, first]
    assert repository.list(limit=2) == [third, second]
    assert repository.list(offset=1, limit=1) == [second]
    assert repository.list(category="safety") == [second]
    assert repository.list(status=DashboardStatus.ACTIVE.value) == [third, first]
    assert repository.list(owner_user_id=owner.id) == [second, first]
    assert repository.list(created_from=datetime(2026, 7, 5, 10, 0, 0)) == [third, second]
    assert repository.list(created_to=datetime(2026, 7, 5, 10, 0, 0)) == [second, first]
    assert repository.list(category="missing") == []
    assert repository.count() == 3
    assert repository.count(owner_user_id=owner.id) == 2
    assert repository.count(category="quality", status=DashboardStatus.ACTIVE.value) == 1


def test_report_definition_repository_create_lookup_update_soft_delete_and_filters(
    db_session: Session,
) -> None:
    repository = ReportDefinitionRepository(db_session)
    owner = create_test_user(db_session)

    report = create_report_definition(repository, owner_user_id=owner.id)
    alias_report = repository.create_report_definition(
        ReportDefinition(code="alias-report", name="Alias report"),
    )
    original_uuid = report.report_uuid

    assert repository.health() is True
    assert repository.get_by_id(report.id) == report
    assert repository.get_by_uuid(original_uuid) == report
    assert repository.get_by_code(report.code) == report
    assert repository.exists(report.id) is True
    assert repository.get_by_id(999) is None
    assert repository.get_by_uuid(uuid4()) is None
    assert repository.get_by_code("missing") is None
    assert repository.exists(999) is False

    updated_report = repository.update(
        report.id,
        {
            "name": "Updated documents summary",
            "default_format": ReportOutputFormat.XLSX.value,
            "status": ReportDefinitionStatus.ARCHIVED.value,
            "query_config": {"select": ["id", "status"]},
            "last_generated_at": datetime(2026, 7, 5, 12, 0, 0),
        },
    )

    assert updated_report is report
    assert report.report_uuid == original_uuid
    assert report.default_format == ReportOutputFormat.XLSX.value
    assert report.last_generated_at == datetime(2026, 7, 5, 12, 0, 0)
    assert repository.update(999, {"name": "Missing"}) is None
    with pytest.raises(ValueError, match="Unsupported report definition update fields: id"):
        repository.update(report.id, {"id": 999})

    assert repository.mark_deleted(report.id) is True
    assert repository.get_by_id(report.id) is None
    assert repository.get_by_id(report.id, include_deleted=True) == report
    assert repository.get_by_uuid(original_uuid) is None
    assert repository.get_by_uuid(original_uuid, include_deleted=True) == report
    assert repository.exists(report.id) is False
    assert repository.exists(report.id, include_deleted=True) is True
    assert repository.list() == [alias_report]
    assert repository.count() == 1
    assert repository.list(include_deleted=True) == [alias_report, report]
    assert repository.count(include_deleted=True) == 2
    assert repository.delete(999) is False


def test_report_definition_repository_list_filters_count_ordering_and_pagination(
    db_session: Session,
) -> None:
    repository = ReportDefinitionRepository(db_session)
    owner = create_test_user(db_session, "report-definition-filter-owner")
    other_owner = create_test_user(db_session, "report-definition-filter-other")

    first = create_report_definition(
        repository,
        code="documents-first",
        category="documents",
        source_module="document_management",
        owner_user_id=owner.id,
        created_at=datetime(2026, 7, 5, 9, 0, 0),
    )
    second = create_report_definition(
        repository,
        code="audit-second",
        name="Audit report",
        category="audit",
        source_module="audit_log",
        status=ReportDefinitionStatus.DRAFT.value,
        default_format=ReportOutputFormat.CSV.value,
        owner_user_id=owner.id,
        created_at=datetime(2026, 7, 5, 10, 0, 0),
    )
    third = create_report_definition(
        repository,
        code="notifications-third",
        name="Notifications report",
        category="notifications",
        source_module="notifications",
        default_format=ReportOutputFormat.HTML.value,
        owner_user_id=other_owner.id,
        created_at=datetime(2026, 7, 5, 11, 0, 0),
    )

    assert repository.list() == [third, second, first]
    assert repository.list(limit=2) == [third, second]
    assert repository.list(offset=1, limit=1) == [second]
    assert repository.list(category="audit") == [second]
    assert repository.list(source_module="notifications") == [third]
    assert repository.list(status=ReportDefinitionStatus.ACTIVE.value) == [third, first]
    assert repository.list(default_format=ReportOutputFormat.CSV.value) == [second]
    assert repository.list(owner_user_id=owner.id) == [second, first]
    assert repository.list(created_from=datetime(2026, 7, 5, 10, 0, 0)) == [third, second]
    assert repository.list(created_to=datetime(2026, 7, 5, 10, 0, 0)) == [second, first]
    assert repository.count() == 3
    assert repository.count(owner_user_id=owner.id) == 2
    assert repository.count(source_module="audit_log", default_format=ReportOutputFormat.CSV.value) == 1


def test_report_run_repository_create_lookup_update_status_filters_and_health(
    db_session: Session,
) -> None:
    definition_repository = ReportDefinitionRepository(db_session)
    run_repository = ReportRunRepository(db_session)
    owner = create_test_user(db_session)
    report = create_report_definition(definition_repository, owner_user_id=owner.id)

    run = create_report_run(run_repository, report_definition_id=report.id, requested_by_user_id=owner.id)
    alias_run = run_repository.create_run(
        ReportRun(report_definition_id=report.id, output_format=ReportOutputFormat.CSV.value),
    )
    original_uuid = run.run_uuid

    assert run_repository.health() is True
    assert run_repository.get_by_id(run.id) == run
    assert run_repository.get_by_uuid(original_uuid) == run
    assert run_repository.exists(run.id) is True
    assert run_repository.get_by_id(999) is None
    assert run_repository.get_by_uuid(uuid4()) is None
    assert run_repository.exists(999) is False

    started_at = datetime(2026, 7, 5, 12, 0, 0)
    completed_at = datetime(2026, 7, 5, 12, 5, 0)
    updated_run = run_repository.mark_status(
        run.id,
        ReportRunStatus.COMPLETED.value,
        started_at=started_at,
        completed_at=completed_at,
        result_summary={"rows": 25},
        row_count=25,
    )

    assert updated_run is run
    assert run.run_uuid == original_uuid
    assert run.status == ReportRunStatus.COMPLETED.value
    assert run.started_at == started_at
    assert run.completed_at == completed_at
    assert run.result_summary == {"rows": 25}
    assert run.row_count == 25
    assert run_repository.update(999, {"status": ReportRunStatus.FAILED.value}) is None
    with pytest.raises(ValueError, match="Unsupported report run update fields: id"):
        run_repository.update(run.id, {"id": 999})

    assert run_repository.list() == [alias_run, run]
    assert run_repository.list(limit=1) == [alias_run]
    assert run_repository.list(offset=1, limit=1) == [run]
    assert run_repository.list(report_definition_id=report.id) == [alias_run, run]
    assert run_repository.list(requested_by_user_id=owner.id) == [run]
    assert run_repository.list(status=ReportRunStatus.COMPLETED.value) == [run]
    assert run_repository.list(output_format=ReportOutputFormat.CSV.value) == [alias_run]
    assert run_repository.list(started_from=started_at, completed_to=completed_at) == [run]
    assert run_repository.count() == 2
    assert run_repository.count(status=ReportRunStatus.COMPLETED.value) == 1
    assert run_repository.count(output_format=ReportOutputFormat.JSON.value) == 0


def test_report_run_repository_date_filters_include_failed_ranges(
    db_session: Session,
) -> None:
    definition_repository = ReportDefinitionRepository(db_session)
    run_repository = ReportRunRepository(db_session)
    report = create_report_definition(definition_repository)

    failed_run = create_report_run(
        run_repository,
        report_definition_id=report.id,
        status=ReportRunStatus.FAILED.value,
        failed_at=datetime(2026, 7, 5, 13, 0, 0),
        failure_reason="Generation failed",
        created_at=datetime(2026, 7, 5, 12, 55, 0),
    )
    create_report_run(
        run_repository,
        report_definition_id=report.id,
        status=ReportRunStatus.QUEUED.value,
        created_at=datetime(2026, 7, 5, 14, 0, 0),
    )

    assert run_repository.list(failed_from=datetime(2026, 7, 5, 12, 59, 0)) == [failed_run]
    assert run_repository.list(failed_to=datetime(2026, 7, 5, 13, 1, 0), status=ReportRunStatus.FAILED.value) == [failed_run]
    assert run_repository.count(failed_from=datetime(2026, 7, 5, 12, 59, 0)) == 1


def test_analytics_snapshot_repository_create_lookup_update_filters_and_health(
    db_session: Session,
) -> None:
    repository = AnalyticsSnapshotRepository(db_session)

    snapshot = create_snapshot(repository)
    alias_snapshot = repository.create_snapshot(
        AnalyticsSnapshot(metric_key="alias.metric", metric_name="Alias metric", value={"count": 1}),
    )
    original_uuid = snapshot.snapshot_uuid

    assert repository.health() is True
    assert repository.get_by_id(snapshot.id) == snapshot
    assert repository.get_by_uuid(original_uuid) == snapshot
    assert repository.exists(snapshot.id) is True
    assert repository.get_by_id(999) is None
    assert repository.get_by_uuid(uuid4()) is None
    assert repository.exists(999) is False

    calculated_at = datetime(2026, 7, 5, 12, 0, 0)
    updated_snapshot = repository.update(
        snapshot.id,
        {
            "metric_name": "Updated total documents",
            "status": AnalyticsSnapshotStatus.STALE.value,
            "value": {"count": 15},
            "dimensions": {"department": "quality"},
            "calculated_at": calculated_at,
        },
    )

    assert updated_snapshot is snapshot
    assert snapshot.snapshot_uuid == original_uuid
    assert snapshot.metric_name == "Updated total documents"
    assert snapshot.status == AnalyticsSnapshotStatus.STALE.value
    assert snapshot.value == {"count": 15}
    assert snapshot.calculated_at == calculated_at
    assert repository.update(999, {"status": AnalyticsSnapshotStatus.FAILED.value}) is None
    with pytest.raises(ValueError, match="Unsupported analytics snapshot update fields: id"):
        repository.update(snapshot.id, {"id": 999})

    assert repository.list() == [alias_snapshot, snapshot]
    assert repository.list(limit=1) == [alias_snapshot]
    assert repository.list(offset=1, limit=1) == [snapshot]
    assert repository.list(metric_key="documents.total") == [snapshot]
    assert repository.list(source_module="document_management") == [snapshot]
    assert repository.list(entity_type="organization") == [snapshot]
    assert repository.list(entity_id="ORG-001") == [snapshot]
    assert repository.list(period=AnalyticsSnapshotPeriod.DAILY.value) == [alias_snapshot, snapshot]
    assert repository.list(status=AnalyticsSnapshotStatus.STALE.value) == [snapshot]
    assert repository.list(calculated_to=calculated_at) == [snapshot]
    assert repository.count() == 2
    assert repository.count(metric_key="documents.total") == 1
    assert repository.count(status=AnalyticsSnapshotStatus.FAILED.value) == 0


def test_analytics_snapshot_repository_period_filters_and_composite_health(
    db_session: Session,
) -> None:
    snapshot_repository = AnalyticsSnapshotRepository(db_session)
    reporting_repository = ReportingAnalyticsRepository(db_session)

    first = create_snapshot(
        snapshot_repository,
        metric_key="documents.daily",
        metric_name="Daily documents",
        period_start=datetime(2026, 7, 5, 0, 0, 0),
        period_end=datetime(2026, 7, 5, 23, 59, 59),
        calculated_at=datetime(2026, 7, 6, 1, 0, 0),
    )
    second = create_snapshot(
        snapshot_repository,
        metric_key="documents.weekly",
        metric_name="Weekly documents",
        period=AnalyticsSnapshotPeriod.WEEKLY.value,
        period_start=datetime(2026, 7, 1, 0, 0, 0),
        period_end=datetime(2026, 7, 7, 23, 59, 59),
        calculated_at=datetime(2026, 7, 6, 2, 0, 0),
    )

    assert reporting_repository.health() is True
    assert snapshot_repository.list(period_start_from=datetime(2026, 7, 5, 0, 0, 0)) == [first]
    assert snapshot_repository.list(period_start_to=datetime(2026, 7, 1, 0, 0, 0)) == [second]
    assert snapshot_repository.list(period_end_from=datetime(2026, 7, 7, 0, 0, 0)) == [second]
    assert snapshot_repository.list(period_end_to=datetime(2026, 7, 5, 23, 59, 59)) == [first]
    assert snapshot_repository.count(period=AnalyticsSnapshotPeriod.WEEKLY.value) == 1
