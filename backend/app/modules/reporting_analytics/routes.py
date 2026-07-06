"""API routes for the Reporting & Analytics module."""

from typing import NoReturn
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.security import get_current_user
from app.db.dependencies import get_db
from app.models import User
from app.modules.reporting_analytics.models import (
    AnalyticsSnapshot,
    DashboardDefinition,
    ReportDefinition,
    ReportRun,
)
from app.modules.reporting_analytics.repository import ReportingAnalyticsRepository
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
from app.modules.reporting_analytics.service import ReportingAnalyticsService

router = APIRouter()


def get_reporting_analytics_service(
    db: Session = Depends(get_db),
) -> ReportingAnalyticsService:
    return ReportingAnalyticsService(ReportingAnalyticsRepository(db))


def raise_not_found(detail: str) -> NoReturn:
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=detail)


@router.get("/health", response_model=ReportingAnalyticsHealthResponse)
def reporting_analytics_health(
    service: ReportingAnalyticsService = Depends(get_reporting_analytics_service),
) -> dict[str, str]:
    return service.health()


@router.get("/dashboards", response_model=DashboardDefinitionListResponse)
def list_dashboards(
    category: str | None = None,
    status: str | None = None,
    owner_user_id: int | None = None,
    include_deleted: bool = False,
    limit: int = 100,
    offset: int = 0,
    service: ReportingAnalyticsService = Depends(get_reporting_analytics_service),
    _: User = Depends(get_current_user),
) -> DashboardDefinitionListResponse:
    filters = {
        "category": category,
        "status": status,
        "owner_user_id": owner_user_id,
        "include_deleted": include_deleted,
    }
    items = service.list_dashboards(**filters, limit=limit, offset=offset)
    total = service.count_dashboards(**filters)
    return DashboardDefinitionListResponse(
        items=items, total=total, limit=limit, offset=offset
    )


@router.post(
    "/dashboards",
    response_model=DashboardDefinitionResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_dashboard(
    payload: DashboardDefinitionCreate,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
) -> DashboardDefinition:
    service = get_reporting_analytics_service(db)
    dashboard = service.create_dashboard(DashboardDefinition(**payload.model_dump()))
    db.commit()
    db.refresh(dashboard)
    return dashboard


@router.get(
    "/dashboards/uuid/{dashboard_uuid}", response_model=DashboardDefinitionResponse
)
def get_dashboard_by_uuid(
    dashboard_uuid: UUID,
    service: ReportingAnalyticsService = Depends(get_reporting_analytics_service),
    _: User = Depends(get_current_user),
) -> DashboardDefinition:
    dashboard = service.get_dashboard_by_uuid(dashboard_uuid)
    if dashboard is None:
        raise_not_found("Dashboard definition not found")
    return dashboard


@router.get("/dashboards/{dashboard_id}", response_model=DashboardDefinitionResponse)
def get_dashboard(
    dashboard_id: int,
    service: ReportingAnalyticsService = Depends(get_reporting_analytics_service),
    _: User = Depends(get_current_user),
) -> DashboardDefinition:
    dashboard = service.get_dashboard_by_id(dashboard_id)
    if dashboard is None:
        raise_not_found("Dashboard definition not found")
    return dashboard


@router.get("/reports", response_model=ReportDefinitionListResponse)
def list_reports(
    category: str | None = None,
    source_module: str | None = None,
    status: str | None = None,
    default_format: str | None = None,
    owner_user_id: int | None = None,
    include_deleted: bool = False,
    limit: int = 100,
    offset: int = 0,
    service: ReportingAnalyticsService = Depends(get_reporting_analytics_service),
    _: User = Depends(get_current_user),
) -> ReportDefinitionListResponse:
    filters = {
        "category": category,
        "source_module": source_module,
        "status": status,
        "default_format": default_format,
        "owner_user_id": owner_user_id,
        "include_deleted": include_deleted,
    }
    items = service.list_report_definitions(**filters, limit=limit, offset=offset)
    total = service.count_report_definitions(**filters)
    return ReportDefinitionListResponse(
        items=items, total=total, limit=limit, offset=offset
    )


@router.post(
    "/reports",
    response_model=ReportDefinitionResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_report(
    payload: ReportDefinitionCreate,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
) -> ReportDefinition:
    service = get_reporting_analytics_service(db)
    report = service.create_report_definition(ReportDefinition(**payload.model_dump()))
    db.commit()
    db.refresh(report)
    return report


@router.get("/reports/uuid/{report_uuid}", response_model=ReportDefinitionResponse)
def get_report_by_uuid(
    report_uuid: UUID,
    service: ReportingAnalyticsService = Depends(get_reporting_analytics_service),
    _: User = Depends(get_current_user),
) -> ReportDefinition:
    report = service.get_report_definition_by_uuid(report_uuid)
    if report is None:
        raise_not_found("Report definition not found")
    return report


@router.get("/reports/{report_id}", response_model=ReportDefinitionResponse)
def get_report(
    report_id: int,
    service: ReportingAnalyticsService = Depends(get_reporting_analytics_service),
    _: User = Depends(get_current_user),
) -> ReportDefinition:
    report = service.get_report_definition_by_id(report_id)
    if report is None:
        raise_not_found("Report definition not found")
    return report


@router.get("/runs", response_model=ReportRunListResponse)
def list_runs(
    report_definition_id: int | None = None,
    requested_by_user_id: int | None = None,
    status: str | None = None,
    output_format: str | None = None,
    limit: int = 100,
    offset: int = 0,
    service: ReportingAnalyticsService = Depends(get_reporting_analytics_service),
    _: User = Depends(get_current_user),
) -> ReportRunListResponse:
    filters = {
        "report_definition_id": report_definition_id,
        "requested_by_user_id": requested_by_user_id,
        "status": status,
        "output_format": output_format,
    }
    items = service.list_report_runs(**filters, limit=limit, offset=offset)
    total = service.count_report_runs(**filters)
    return ReportRunListResponse(items=items, total=total, limit=limit, offset=offset)


@router.post(
    "/runs", response_model=ReportRunResponse, status_code=status.HTTP_201_CREATED
)
def create_run(
    payload: ReportRunCreate,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
) -> ReportRun:
    service = get_reporting_analytics_service(db)
    run = service.create_report_run(ReportRun(**payload.model_dump()))
    db.commit()
    db.refresh(run)
    return run


@router.get("/runs/uuid/{run_uuid}", response_model=ReportRunResponse)
def get_run_by_uuid(
    run_uuid: UUID,
    service: ReportingAnalyticsService = Depends(get_reporting_analytics_service),
    _: User = Depends(get_current_user),
) -> ReportRun:
    run = service.get_report_run_by_uuid(run_uuid)
    if run is None:
        raise_not_found("Report run not found")
    return run


@router.get("/runs/{run_id}", response_model=ReportRunResponse)
def get_run(
    run_id: int,
    service: ReportingAnalyticsService = Depends(get_reporting_analytics_service),
    _: User = Depends(get_current_user),
) -> ReportRun:
    run = service.get_report_run_by_id(run_id)
    if run is None:
        raise_not_found("Report run not found")
    return run


@router.get("/snapshots", response_model=AnalyticsSnapshotListResponse)
def list_snapshots(
    metric_key: str | None = None,
    source_module: str | None = None,
    entity_type: str | None = None,
    entity_id: str | None = None,
    period: str | None = None,
    status: str | None = None,
    limit: int = 100,
    offset: int = 0,
    service: ReportingAnalyticsService = Depends(get_reporting_analytics_service),
    _: User = Depends(get_current_user),
) -> AnalyticsSnapshotListResponse:
    filters = {
        "metric_key": metric_key,
        "source_module": source_module,
        "entity_type": entity_type,
        "entity_id": entity_id,
        "period": period,
        "status": status,
    }
    items = service.list_analytics_snapshots(**filters, limit=limit, offset=offset)
    total = service.count_analytics_snapshots(**filters)
    return AnalyticsSnapshotListResponse(
        items=items, total=total, limit=limit, offset=offset
    )


@router.post(
    "/snapshots",
    response_model=AnalyticsSnapshotResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_snapshot(
    payload: AnalyticsSnapshotCreate,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
) -> AnalyticsSnapshot:
    service = get_reporting_analytics_service(db)
    snapshot = service.create_analytics_snapshot(
        AnalyticsSnapshot(**payload.model_dump())
    )
    db.commit()
    db.refresh(snapshot)
    return snapshot


@router.get("/snapshots/uuid/{snapshot_uuid}", response_model=AnalyticsSnapshotResponse)
def get_snapshot_by_uuid(
    snapshot_uuid: UUID,
    service: ReportingAnalyticsService = Depends(get_reporting_analytics_service),
    _: User = Depends(get_current_user),
) -> AnalyticsSnapshot:
    snapshot = service.get_analytics_snapshot_by_uuid(snapshot_uuid)
    if snapshot is None:
        raise_not_found("Analytics snapshot not found")
    return snapshot


@router.get("/snapshots/{snapshot_id}", response_model=AnalyticsSnapshotResponse)
def get_snapshot(
    snapshot_id: int,
    service: ReportingAnalyticsService = Depends(get_reporting_analytics_service),
    _: User = Depends(get_current_user),
) -> AnalyticsSnapshot:
    snapshot = service.get_analytics_snapshot_by_id(snapshot_id)
    if snapshot is None:
        raise_not_found("Analytics snapshot not found")
    return snapshot
