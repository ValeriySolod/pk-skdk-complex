"""Database-backed API routes for Monitoring & Health."""
from typing import Any, NoReturn
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from app.core.security import get_current_user
from app.db.dependencies import get_db
from app.models import User
from .models import HealthCheckRecord, MonitoringMetric, SystemIncident
from .repository import MonitoringHealthRepository
from .schemas import *
from .service import MonitoringHealthService

router = APIRouter()

def get_monitoring_health_service(db: Session = Depends(get_db)) -> MonitoringHealthService:
    return MonitoringHealthService(MonitoringHealthRepository(db))

def raise_not_found(detail: str) -> NoReturn:
    raise HTTPException(status_code=404, detail=detail)

def raise_bad_request(exc: ValueError) -> NoReturn:
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail=str(exc),
    ) from exc

def _write(db: Session, create: Any, detail: str) -> Any:
    try:
        result = create(); db.commit(); db.refresh(result); return result
    except ValueError as exc:
        db.rollback(); raise_bad_request(exc)
    except IntegrityError as exc:
        db.rollback(); raise HTTPException(status_code=409, detail=detail) from exc

def _commit_update(db: Session, update: Any, detail: str) -> Any:
    try:
        result = update()
        if result is None:
            return None
        db.commit()
        db.refresh(result)
        return result
    except ValueError as exc:
        db.rollback(); raise_bad_request(exc)
    except IntegrityError as exc:
        db.rollback(); raise HTTPException(status_code=409, detail=detail) from exc

@router.get("/health", response_model=MonitoringHealthHealthRead)
def module_health(service: MonitoringHealthService = Depends(get_monitoring_health_service), _: User = Depends(get_current_user)) -> MonitoringHealthHealthRead:
    return service.health()

def _list(service: MonitoringHealthService, filters: BaseModel, list_name: str, count_name: str, response: type[BaseModel]) -> BaseModel:
    values = filters.model_dump()
    try:
        items = getattr(service, list_name)(**values)
        total = getattr(service, count_name)(**{k:v for k,v in values.items() if k not in {"limit", "offset"}})
    except ValueError as exc:
        raise_bad_request(exc)
    return response(items=items, total=total, limit=values["limit"], offset=values["offset"])

@router.get("/health-checks", response_model=HealthCheckListResponse)
def list_health_checks(filters: HealthCheckFilterParams = Depends(), service: MonitoringHealthService = Depends(get_monitoring_health_service), _: User = Depends(get_current_user)) -> BaseModel:
    return _list(service, filters, "list_health_checks", "count_health_checks", HealthCheckListResponse)

@router.post("/health-checks", response_model=HealthCheckRead, status_code=201)
def create_health_check(payload: HealthCheckCreate, db: Session = Depends(get_db), _: User = Depends(get_current_user)) -> HealthCheckRecord:
    service=get_monitoring_health_service(db); return _write(db, lambda: service.create_health_check(payload.model_dump(exclude_none=True)), "Health check could not be persisted")

@router.get("/health-checks/uuid/{record_uuid}", response_model=HealthCheckRead)
def get_health_check_uuid(record_uuid: UUID, service: MonitoringHealthService=Depends(get_monitoring_health_service), _: User=Depends(get_current_user)) -> HealthCheckRecord:
    result=service.get_health_check_by_uuid(record_uuid)
    if result is None: raise_not_found("Health check not found")
    return result

@router.get("/health-checks/{record_id}", response_model=HealthCheckRead)
def get_health_check(record_id: int, service: MonitoringHealthService=Depends(get_monitoring_health_service), _: User=Depends(get_current_user)) -> HealthCheckRecord:
    result=service.get_health_check(record_id)
    if result is None: raise_not_found("Health check not found")
    return result

@router.patch("/health-checks/{record_id}", response_model=HealthCheckRead)
def update_health_check(record_id: int, payload: HealthCheckUpdate, db: Session=Depends(get_db), _: User=Depends(get_current_user)) -> HealthCheckRecord:
    service=get_monitoring_health_service(db)
    result=_commit_update(db, lambda: service.update_health_check(record_id, payload.model_dump(exclude_unset=True)), "Health check could not be updated")
    if result is None: raise_not_found("Health check not found")
    return result

@router.get("/metrics", response_model=MonitoringMetricListResponse)
def list_metrics(filters: MonitoringMetricFilterParams=Depends(), service: MonitoringHealthService=Depends(get_monitoring_health_service), _: User=Depends(get_current_user)) -> BaseModel:
    return _list(service, filters, "list_metrics", "count_metrics", MonitoringMetricListResponse)

@router.post("/metrics", response_model=MonitoringMetricRead, status_code=201)
def create_metric(payload: MonitoringMetricCreate, db: Session=Depends(get_db), _: User=Depends(get_current_user)) -> MonitoringMetric:
    service=get_monitoring_health_service(db); return _write(db, lambda: service.create_metric(payload.model_dump(exclude_none=True)), "Metric could not be persisted")

@router.get("/metrics/uuid/{metric_uuid}", response_model=MonitoringMetricRead)
def get_metric_uuid(metric_uuid: UUID, service: MonitoringHealthService=Depends(get_monitoring_health_service), _: User=Depends(get_current_user)) -> MonitoringMetric:
    result=service.get_metric_by_uuid(metric_uuid)
    if result is None: raise_not_found("Metric not found")
    return result

@router.get("/metrics/{metric_id}", response_model=MonitoringMetricRead)
def get_metric(metric_id: int, service: MonitoringHealthService=Depends(get_monitoring_health_service), _: User=Depends(get_current_user)) -> MonitoringMetric:
    result=service.get_metric(metric_id)
    if result is None: raise_not_found("Metric not found")
    return result

@router.patch("/metrics/{metric_id}", response_model=MonitoringMetricRead)
def update_metric(metric_id: int, payload: MonitoringMetricUpdate, db: Session=Depends(get_db), _: User=Depends(get_current_user)) -> MonitoringMetric:
    service=get_monitoring_health_service(db)
    result=_commit_update(db, lambda: service.update_metric(metric_id, payload.model_dump(exclude_unset=True)), "Metric could not be updated")
    if result is None: raise_not_found("Metric not found")
    return result

@router.get("/incidents", response_model=SystemIncidentListResponse)
def list_incidents(filters: SystemIncidentFilterParams=Depends(), service: MonitoringHealthService=Depends(get_monitoring_health_service), _: User=Depends(get_current_user)) -> BaseModel:
    return _list(service, filters, "list_incidents", "count_incidents", SystemIncidentListResponse)

@router.post("/incidents", response_model=SystemIncidentRead, status_code=201)
def create_incident(payload: SystemIncidentCreate, db: Session=Depends(get_db), _: User=Depends(get_current_user)) -> SystemIncident:
    service=get_monitoring_health_service(db); return _write(db, lambda: service.create_incident(payload.model_dump(exclude_none=True)), "Incident could not be persisted")

@router.get("/incidents/uuid/{incident_uuid}", response_model=SystemIncidentRead)
def get_incident_uuid(incident_uuid: UUID, service: MonitoringHealthService=Depends(get_monitoring_health_service), _: User=Depends(get_current_user)) -> SystemIncident:
    result=service.get_incident_by_uuid(incident_uuid)
    if result is None: raise_not_found("Incident not found")
    return result

@router.get("/incidents/{incident_id}", response_model=SystemIncidentRead)
def get_incident(incident_id: int, service: MonitoringHealthService=Depends(get_monitoring_health_service), _: User=Depends(get_current_user)) -> SystemIncident:
    result=service.get_incident(incident_id)
    if result is None: raise_not_found("Incident not found")
    return result

@router.patch("/incidents/{incident_id}", response_model=SystemIncidentRead)
def update_incident(incident_id: int, payload: SystemIncidentUpdate, db: Session=Depends(get_db), _: User=Depends(get_current_user)) -> SystemIncident:
    service=get_monitoring_health_service(db)
    result=_commit_update(db, lambda: service.update_incident(incident_id, payload.model_dump(exclude_unset=True)), "Incident could not be updated")
    if result is None: raise_not_found("Incident not found")
    return result

@router.patch("/incidents/{incident_id}/status", response_model=SystemIncidentRead)
def update_incident_status(incident_id: int, payload: SystemIncidentStatusUpdate, db: Session=Depends(get_db), _: User=Depends(get_current_user)) -> SystemIncident:
    service=get_monitoring_health_service(db)
    result=_commit_update(db, lambda: service.mark_incident_status(incident_id, payload.status, **payload.model_dump(exclude={"status"}, exclude_unset=True)), "Incident status could not be updated")
    if result is None: raise_not_found("Incident not found")
    return result
