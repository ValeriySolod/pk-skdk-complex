"""API contract tests for the Reporting & Analytics module."""

from __future__ import annotations

from datetime import UTC, datetime
from uuid import uuid4

from fastapi.testclient import TestClient

from app.main import app
from app.modules.reporting_analytics.models import (
    AnalyticsSnapshotPeriod,
    AnalyticsSnapshotStatus,
    DashboardStatus,
    ReportDefinitionStatus,
    ReportOutputFormat,
    ReportRunStatus,
)
from app.modules.reporting_analytics.schemas import (
    AnalyticsSnapshotCreate,
    AnalyticsSnapshotListResponse,
    AnalyticsSnapshotResponse,
    DashboardDefinitionCreate,
    DashboardDefinitionListResponse,
    DashboardDefinitionResponse,
    ReportDefinitionCreate,
    ReportDefinitionListResponse,
    ReportDefinitionResponse,
    ReportingAnalyticsHealthResponse,
    ReportRunCreate,
    ReportRunListResponse,
    ReportRunResponse,
)


client = TestClient(app)


def test_reporting_analytics_health_route_contract() -> None:
    response = client.get("/api/v1/reporting-analytics/health")

    assert response.status_code == 200
    assert response.json() == {
        "status": "healthy",
        "module": "reporting_analytics",
    }

    parsed = ReportingAnalyticsHealthResponse.model_validate(response.json())
    assert parsed.status == "healthy"
    assert parsed.module == "reporting_analytics"


def test_reporting_analytics_openapi_contract_contains_health_route() -> None:
    schema = client.get("/openapi.json").json()

    path = schema["paths"]["/api/v1/reporting-analytics/health"]["get"]
    assert path["tags"] == ["Reporting & Analytics"]
    assert path["responses"]["200"]["description"] == "Successful Response"

    response_schema = path["responses"]["200"]["content"]["application/json"]["schema"]
    assert response_schema["$ref"].endswith("/ReportingAnalyticsHealthResponse")


def test_dashboard_definition_schemas_contract() -> None:
    created_at = datetime.now(UTC)

    create_payload = DashboardDefinitionCreate(
        code="operations-dashboard",
        name="Operations Dashboard",
        description="Operational metrics dashboard",
        category="operations",
        status=DashboardStatus.ACTIVE,
        owner_user_id=10,
        layout_config={"columns": 12},
        widget_config={"widgets": [{"type": "metric"}]},
        filter_config={"region": "global"},
    )

    assert create_payload.status == DashboardStatus.ACTIVE
    assert create_payload.layout_config == {"columns": 12}

    response = DashboardDefinitionResponse(
        id=1,
        dashboard_uuid=uuid4(),
        created_at=created_at,
        updated_at=created_at,
        **create_payload.model_dump(),
    )

    list_response = DashboardDefinitionListResponse(
        items=[response],
        total=1,
        limit=10,
        offset=0,
    )

    assert list_response.total == 1
    assert list_response.items[0].code == "operations-dashboard"


def test_report_definition_schemas_contract() -> None:
    created_at = datetime.now(UTC)

    create_payload = ReportDefinitionCreate(
        code="monthly-operations-report",
        name="Monthly Operations Report",
        description="Monthly operational report",
        category="operations",
        source_module="orders",
        status=ReportDefinitionStatus.ACTIVE,
        default_format=ReportOutputFormat.PDF,
        owner_user_id=10,
        query_config={"source": "orders"},
        filter_schema={"month": {"type": "string"}},
        layout_config={"template": "monthly"},
    )

    assert create_payload.status == ReportDefinitionStatus.ACTIVE
    assert create_payload.default_format == ReportOutputFormat.PDF

    response = ReportDefinitionResponse(
        id=1,
        report_uuid=uuid4(),
        last_generated_at=None,
        created_at=created_at,
        updated_at=created_at,
        **create_payload.model_dump(),
    )

    list_response = ReportDefinitionListResponse(
        items=[response],
        total=1,
        limit=10,
        offset=0,
    )

    assert list_response.total == 1
    assert list_response.items[0].source_module == "orders"


def test_report_run_schemas_contract() -> None:
    created_at = datetime.now(UTC)

    create_payload = ReportRunCreate(
        report_definition_id=1,
        requested_by_user_id=10,
        file_object_id=None,
        status=ReportRunStatus.QUEUED,
        output_format=ReportOutputFormat.XLSX,
        parameters={"month": "2026-07"},
        result_summary=None,
        row_count=0,
    )

    assert create_payload.status == ReportRunStatus.QUEUED
    assert create_payload.output_format == ReportOutputFormat.XLSX

    response = ReportRunResponse(
        id=1,
        run_uuid=uuid4(),
        created_at=created_at,
        updated_at=created_at,
        **create_payload.model_dump(),
    )

    list_response = ReportRunListResponse(
        items=[response],
        total=1,
        limit=10,
        offset=0,
    )

    assert list_response.total == 1
    assert list_response.items[0].report_definition_id == 1


def test_analytics_snapshot_schemas_contract() -> None:
    created_at = datetime.now(UTC)

    create_payload = AnalyticsSnapshotCreate(
        metric_key="orders.total",
        metric_name="Total Orders",
        source_module="orders",
        entity_type="tenant",
        entity_id="global",
        period=AnalyticsSnapshotPeriod.DAILY,
        status=AnalyticsSnapshotStatus.READY,
        value={"count": 100},
        dimensions={"region": "global"},
        period_start=created_at,
        period_end=created_at,
    )

    assert create_payload.period == AnalyticsSnapshotPeriod.DAILY
    assert create_payload.status == AnalyticsSnapshotStatus.READY

    response = AnalyticsSnapshotResponse(
        id=1,
        snapshot_uuid=uuid4(),
        calculated_at=created_at,
        created_at=created_at,
        updated_at=created_at,
        **create_payload.model_dump(),
    )

    list_response = AnalyticsSnapshotListResponse(
        items=[response],
        total=1,
        limit=10,
        offset=0,
    )

    assert list_response.total == 1
    assert list_response.items[0].metric_key == "orders.total"
