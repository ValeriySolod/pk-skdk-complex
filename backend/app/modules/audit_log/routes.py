from typing import NoReturn
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.security import get_current_user
from app.db.dependencies import get_db
from app.models import User
from app.modules.audit_log.models import AuditLogEvent
from app.modules.audit_log.repository import AuditLogRepository
from app.modules.audit_log.schemas import (
    AuditLogCreate,
    AuditLogFilterParams,
    AuditLogHealthRead,
    AuditLogListResponse,
    AuditLogResponse,
)
from app.modules.audit_log.service import AuditLogService


router = APIRouter()


def get_audit_log_service(
    db: Session = Depends(get_db),
) -> AuditLogService:
    repository = AuditLogRepository(db)
    return AuditLogService(repository)


def raise_not_found(detail: str) -> NoReturn:
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=detail,
    )


@router.get("/health", response_model=AuditLogHealthRead)
def module_health(
    service: AuditLogService = Depends(get_audit_log_service),
    _: User = Depends(get_current_user),
) -> dict[str, str]:
    return service.health()


@router.get("/events", response_model=AuditLogListResponse)
def list_events(
    filters: AuditLogFilterParams = Depends(),
    service: AuditLogService = Depends(get_audit_log_service),
    _: User = Depends(get_current_user),
) -> AuditLogListResponse:
    filter_values = filters.model_dump()
    events = service.list_events(**filter_values)
    total = service.count_events(
        **{
            key: value
            for key, value in filter_values.items()
            if key not in {"limit", "offset"}
        },
    )
    return AuditLogListResponse(
        items=events,
        total=total,
        limit=filters.limit,
        offset=filters.offset,
    )


@router.post(
    "/events",
    response_model=AuditLogResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_event(
    payload: AuditLogCreate,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
) -> AuditLogEvent:
    service = get_audit_log_service(db)
    audit_event = service.create_event(AuditLogEvent(**payload.model_dump()))
    db.commit()
    db.refresh(audit_event)
    return audit_event


@router.get("/events/uuid/{event_uuid}", response_model=AuditLogResponse)
def get_event_by_uuid(
    event_uuid: UUID,
    service: AuditLogService = Depends(get_audit_log_service),
    _: User = Depends(get_current_user),
) -> AuditLogEvent:
    audit_event = service.get_event_by_uuid(event_uuid)
    if audit_event is None:
        raise_not_found("Audit log event not found")
    return audit_event


@router.get("/events/{event_id}", response_model=AuditLogResponse)
def get_event(
    event_id: int,
    service: AuditLogService = Depends(get_audit_log_service),
    _: User = Depends(get_current_user),
) -> AuditLogEvent:
    audit_event = service.get_event(event_id)
    if audit_event is None:
        raise_not_found("Audit log event not found")
    return audit_event
