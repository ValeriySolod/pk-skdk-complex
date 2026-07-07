"""API routes for the Administration module."""

from typing import NoReturn
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.security import get_current_user
from app.db.dependencies import get_db
from app.models import User
from app.modules.administration.models import (
    AdminActionEvent,
    AdministrationReference,
    MaintenanceTask,
)
from app.modules.administration.schemas import (
    AdminActionEventCreate,
    AdminActionEventListResponse,
    AdminActionEventRead,
    AdministrationHealthRead,
    AdministrationReferenceCreate,
    AdministrationReferenceListResponse,
    AdministrationReferenceRead,
    MaintenanceTaskCreate,
    MaintenanceTaskListResponse,
    MaintenanceTaskRead,
)
from app.modules.administration.service import AdministrationService

router = APIRouter()


def get_administration_service(
    db: Session = Depends(get_db),
) -> AdministrationService:
    return AdministrationService(db)


def raise_not_found(detail: str) -> NoReturn:
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=detail)


@router.get("/health", response_model=AdministrationHealthRead)
def module_health(
    service: AdministrationService = Depends(get_administration_service),
) -> dict[str, object]:
    return service.health()


@router.get("/references", response_model=AdministrationReferenceListResponse)
def list_references(
    catalog: str | None = None,
    status: str | None = None,
    include_deleted: bool = False,
    limit: int = 100,
    offset: int = 0,
    service: AdministrationService = Depends(get_administration_service),
    _: User = Depends(get_current_user),
) -> AdministrationReferenceListResponse:
    filters = {"catalog": catalog, "status": status, "include_deleted": include_deleted}
    items = service.list_references(**filters, limit=limit, offset=offset)
    total = service.count_references(**filters)
    return AdministrationReferenceListResponse(
        items=items, total=total, limit=limit, offset=offset
    )


@router.post(
    "/references",
    response_model=AdministrationReferenceRead,
    status_code=status.HTTP_201_CREATED,
)
def create_reference(
    payload: AdministrationReferenceCreate,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
) -> AdministrationReference:
    service = get_administration_service(db)
    reference = service.create_reference(payload.model_dump())
    db.commit()
    db.refresh(reference)
    return reference


@router.get(
    "/references/uuid/{reference_uuid}", response_model=AdministrationReferenceRead
)
def get_reference_by_uuid(
    reference_uuid: UUID,
    service: AdministrationService = Depends(get_administration_service),
    _: User = Depends(get_current_user),
) -> AdministrationReference:
    reference = service.get_reference_by_uuid(reference_uuid)
    if reference is None:
        raise_not_found("Administration reference not found")
    return reference


@router.get("/references/{reference_id}", response_model=AdministrationReferenceRead)
def get_reference(
    reference_id: int,
    service: AdministrationService = Depends(get_administration_service),
    _: User = Depends(get_current_user),
) -> AdministrationReference:
    reference = service.get_reference(reference_id)
    if reference is None:
        raise_not_found("Administration reference not found")
    return reference


@router.get("/maintenance-tasks", response_model=MaintenanceTaskListResponse)
def list_maintenance_tasks(
    operation_type: str | None = None,
    status: str | None = None,
    requested_by_user_id: int | None = None,
    include_deleted: bool = False,
    limit: int = 100,
    offset: int = 0,
    service: AdministrationService = Depends(get_administration_service),
    _: User = Depends(get_current_user),
) -> MaintenanceTaskListResponse:
    filters = {
        "operation_type": operation_type,
        "status": status,
        "requested_by_user_id": requested_by_user_id,
        "include_deleted": include_deleted,
    }
    items = service.list_maintenance_tasks(**filters, limit=limit, offset=offset)
    total = service.count_maintenance_tasks(**filters)
    return MaintenanceTaskListResponse(
        items=items, total=total, limit=limit, offset=offset
    )


@router.post(
    "/maintenance-tasks",
    response_model=MaintenanceTaskRead,
    status_code=status.HTTP_201_CREATED,
)
def create_maintenance_task(
    payload: MaintenanceTaskCreate,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
) -> MaintenanceTask:
    service = get_administration_service(db)
    data = payload.model_dump()
    task = service.create_maintenance_task(
        {
            "operation_type": data["code"],
            "operation_name": data["title"],
            "status": data["status"],
            "payload": data.get("metadata_json"),
            "completed_at": data.get("completed_at"),
        }
    )
    db.commit()
    db.refresh(task)
    return task


@router.get("/maintenance-tasks/uuid/{task_uuid}", response_model=MaintenanceTaskRead)
def get_maintenance_task_by_uuid(
    task_uuid: UUID,
    service: AdministrationService = Depends(get_administration_service),
    _: User = Depends(get_current_user),
) -> MaintenanceTask:
    task = service.get_maintenance_task_by_uuid(task_uuid)
    if task is None:
        raise_not_found("Maintenance task not found")
    return task


@router.get("/maintenance-tasks/{task_id}", response_model=MaintenanceTaskRead)
def get_maintenance_task(
    task_id: int,
    service: AdministrationService = Depends(get_administration_service),
    _: User = Depends(get_current_user),
) -> MaintenanceTask:
    task = service.get_maintenance_task(task_id)
    if task is None:
        raise_not_found("Maintenance task not found")
    return task


@router.get("/action-events", response_model=AdminActionEventListResponse)
def list_action_events(
    action: str | None = None,
    target_type: str | None = None,
    target_id: str | None = None,
    actor_user_id: int | None = None,
    limit: int = 100,
    offset: int = 0,
    service: AdministrationService = Depends(get_administration_service),
    _: User = Depends(get_current_user),
) -> AdminActionEventListResponse:
    filters = {
        "action": action,
        "target_type": target_type,
        "target_id": target_id,
        "actor_user_id": actor_user_id,
    }
    items = service.list_action_events(**filters, limit=limit, offset=offset)
    total = service.count_action_events(**filters)
    return AdminActionEventListResponse(
        items=items, total=total, limit=limit, offset=offset
    )


@router.post(
    "/action-events",
    response_model=AdminActionEventRead,
    status_code=status.HTTP_201_CREATED,
)
def create_action_event(
    payload: AdminActionEventCreate,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
) -> AdminActionEvent:
    service = get_administration_service(db)
    data = payload.model_dump()
    event = service.create_action_event(
        {
            "actor_user_id": data.get("actor_user_id"),
            "action_type": data["action"],
            "target_type": data["target_type"],
            "target_id": data.get("target_id"),
            "resource": data.get("description"),
            "details": data.get("metadata_json") or {},
        }
    )
    db.commit()
    db.refresh(event)
    return event


@router.get("/action-events/uuid/{event_uuid}", response_model=AdminActionEventRead)
def get_action_event_by_uuid(
    event_uuid: UUID,
    service: AdministrationService = Depends(get_administration_service),
    _: User = Depends(get_current_user),
) -> AdminActionEvent:
    event = service.get_action_event_by_uuid(event_uuid)
    if event is None:
        raise_not_found("Administration action event not found")
    return event


@router.get("/action-events/{event_id}", response_model=AdminActionEventRead)
def get_action_event(
    event_id: int,
    service: AdministrationService = Depends(get_administration_service),
    _: User = Depends(get_current_user),
) -> AdminActionEvent:
    event = service.get_action_event(event_id)
    if event is None:
        raise_not_found("Administration action event not found")
    return event
