"""API routes for the Integrations module."""

from typing import NoReturn
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.security import get_current_user
from app.db.dependencies import get_db
from app.models import User
from app.modules.integrations.models import (
    IntegrationConnection,
    IntegrationEvent,
    IntegrationProvider,
    IntegrationSyncJob,
)
from app.modules.integrations.repository import IntegrationsRepository
from app.modules.integrations.schemas import (
    IntegrationConnectionCreate,
    IntegrationConnectionFilterParams,
    IntegrationConnectionListResponse,
    IntegrationConnectionResponse,
    IntegrationConnectionUpdate,
    IntegrationEventCreate,
    IntegrationEventFilterParams,
    IntegrationEventListResponse,
    IntegrationEventResponse,
    IntegrationEventUpdate,
    IntegrationProviderCreate,
    IntegrationProviderFilterParams,
    IntegrationProviderListResponse,
    IntegrationProviderResponse,
    IntegrationProviderUpdate,
    IntegrationSyncJobCreate,
    IntegrationSyncJobFilterParams,
    IntegrationSyncJobListResponse,
    IntegrationSyncJobResponse,
    IntegrationSyncJobUpdate,
    IntegrationsHealthRead,
)
from app.modules.integrations.service import IntegrationsService

router = APIRouter()


def get_integrations_service(
    db: Session = Depends(get_db),
) -> IntegrationsService:
    repository = IntegrationsRepository(db)
    return IntegrationsService(repository)


def raise_not_found(detail: str) -> NoReturn:
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=detail)


def duplicate_integration_error(detail: str) -> HTTPException:
    return HTTPException(status_code=status.HTTP_409_CONFLICT, detail=detail)


@router.get("/health", response_model=IntegrationsHealthRead)
def module_health(
    service: IntegrationsService = Depends(get_integrations_service),
    _: User = Depends(get_current_user),
) -> IntegrationsHealthRead:
    return service.health()


@router.get("/providers", response_model=IntegrationProviderListResponse)
def list_providers(
    filters: IntegrationProviderFilterParams = Depends(),
    service: IntegrationsService = Depends(get_integrations_service),
    _: User = Depends(get_current_user),
) -> IntegrationProviderListResponse:
    filter_values = filters.model_dump()
    items = service.list_providers(**filter_values)
    total = service.count_providers(
        **{
            key: value
            for key, value in filter_values.items()
            if key not in {"limit", "offset"}
        },
    )
    return IntegrationProviderListResponse(
        items=items,
        total=total,
        limit=filters.limit,
        offset=filters.offset,
    )


@router.post(
    "/providers",
    response_model=IntegrationProviderResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_provider(
    payload: IntegrationProviderCreate,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
) -> IntegrationProvider:
    service = get_integrations_service(db)
    try:
        provider = service.create_provider(payload.model_dump())
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise duplicate_integration_error(
            "Integration provider with this code already exists"
        ) from exc
    db.refresh(provider)
    return provider


@router.get(
    "/providers/uuid/{provider_uuid}",
    response_model=IntegrationProviderResponse,
)
def get_provider_by_uuid(
    provider_uuid: UUID,
    service: IntegrationsService = Depends(get_integrations_service),
    _: User = Depends(get_current_user),
) -> IntegrationProvider:
    provider = service.get_provider_by_uuid(provider_uuid)
    if provider is None:
        raise_not_found("Integration provider not found")
    return provider


@router.get("/providers/{provider_id}", response_model=IntegrationProviderResponse)
def get_provider(
    provider_id: int,
    service: IntegrationsService = Depends(get_integrations_service),
    _: User = Depends(get_current_user),
) -> IntegrationProvider:
    provider = service.get_provider(provider_id)
    if provider is None:
        raise_not_found("Integration provider not found")
    return provider


@router.patch("/providers/{provider_id}", response_model=IntegrationProviderResponse)
def update_provider(
    provider_id: int,
    payload: IntegrationProviderUpdate,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
) -> IntegrationProvider:
    service = get_integrations_service(db)
    try:
        provider = service.update_provider(
            provider_id,
            payload.model_dump(exclude_unset=True),
        )
        if provider is None:
            raise_not_found("Integration provider not found")
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise duplicate_integration_error(
            "Integration provider with this code already exists"
        ) from exc
    db.refresh(provider)
    return provider


@router.delete("/providers/{provider_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_provider(
    provider_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
) -> Response:
    service = get_integrations_service(db)
    deleted = service.delete_provider(provider_id)
    if not deleted:
        raise_not_found("Integration provider not found")
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/connections", response_model=IntegrationConnectionListResponse)
def list_connections(
    filters: IntegrationConnectionFilterParams = Depends(),
    service: IntegrationsService = Depends(get_integrations_service),
    _: User = Depends(get_current_user),
) -> IntegrationConnectionListResponse:
    filter_values = filters.model_dump()
    items = service.list_connections(**filter_values)
    total = service.count_connections(
        **{
            key: value
            for key, value in filter_values.items()
            if key not in {"limit", "offset"}
        },
    )
    return IntegrationConnectionListResponse(
        items=items,
        total=total,
        limit=filters.limit,
        offset=filters.offset,
    )


@router.post(
    "/connections",
    response_model=IntegrationConnectionResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_connection(
    payload: IntegrationConnectionCreate,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
) -> IntegrationConnection:
    service = get_integrations_service(db)
    try:
        connection = service.create_connection(payload.model_dump())
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise duplicate_integration_error(
            "Integration connection with this provider and name already exists"
        ) from exc
    db.refresh(connection)
    return connection


@router.get(
    "/connections/uuid/{connection_uuid}",
    response_model=IntegrationConnectionResponse,
)
def get_connection_by_uuid(
    connection_uuid: UUID,
    service: IntegrationsService = Depends(get_integrations_service),
    _: User = Depends(get_current_user),
) -> IntegrationConnection:
    connection = service.get_connection_by_uuid(connection_uuid)
    if connection is None:
        raise_not_found("Integration connection not found")
    return connection


@router.get(
    "/connections/{connection_id}",
    response_model=IntegrationConnectionResponse,
)
def get_connection(
    connection_id: int,
    service: IntegrationsService = Depends(get_integrations_service),
    _: User = Depends(get_current_user),
) -> IntegrationConnection:
    connection = service.get_connection(connection_id)
    if connection is None:
        raise_not_found("Integration connection not found")
    return connection


@router.patch(
    "/connections/{connection_id}",
    response_model=IntegrationConnectionResponse,
)
def update_connection(
    connection_id: int,
    payload: IntegrationConnectionUpdate,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
) -> IntegrationConnection:
    service = get_integrations_service(db)
    try:
        connection = service.update_connection(
            connection_id,
            payload.model_dump(exclude_unset=True),
        )
        if connection is None:
            raise_not_found("Integration connection not found")
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise duplicate_integration_error(
            "Integration connection with this provider and name already exists"
        ) from exc
    db.refresh(connection)
    return connection


@router.delete("/connections/{connection_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_connection(
    connection_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
) -> Response:
    service = get_integrations_service(db)
    deleted = service.delete_connection(connection_id)
    if not deleted:
        raise_not_found("Integration connection not found")
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/sync-jobs", response_model=IntegrationSyncJobListResponse)
def list_sync_jobs(
    filters: IntegrationSyncJobFilterParams = Depends(),
    service: IntegrationsService = Depends(get_integrations_service),
    _: User = Depends(get_current_user),
) -> IntegrationSyncJobListResponse:
    filter_values = filters.model_dump()
    items = service.list_sync_jobs(**filter_values)
    total = service.count_sync_jobs(
        **{
            key: value
            for key, value in filter_values.items()
            if key not in {"limit", "offset"}
        },
    )
    return IntegrationSyncJobListResponse(
        items=items,
        total=total,
        limit=filters.limit,
        offset=filters.offset,
    )


@router.post(
    "/sync-jobs",
    response_model=IntegrationSyncJobResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_sync_job(
    payload: IntegrationSyncJobCreate,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
) -> IntegrationSyncJob:
    service = get_integrations_service(db)
    job = service.create_sync_job(payload.model_dump())
    db.commit()
    db.refresh(job)
    return job


@router.get(
    "/sync-jobs/uuid/{job_uuid}",
    response_model=IntegrationSyncJobResponse,
)
def get_sync_job_by_uuid(
    job_uuid: UUID,
    service: IntegrationsService = Depends(get_integrations_service),
    _: User = Depends(get_current_user),
) -> IntegrationSyncJob:
    job = service.get_sync_job_by_uuid(job_uuid)
    if job is None:
        raise_not_found("Integration sync job not found")
    return job


@router.get("/sync-jobs/{job_id}", response_model=IntegrationSyncJobResponse)
def get_sync_job(
    job_id: int,
    service: IntegrationsService = Depends(get_integrations_service),
    _: User = Depends(get_current_user),
) -> IntegrationSyncJob:
    job = service.get_sync_job(job_id)
    if job is None:
        raise_not_found("Integration sync job not found")
    return job


@router.patch("/sync-jobs/{job_id}", response_model=IntegrationSyncJobResponse)
def update_sync_job(
    job_id: int,
    payload: IntegrationSyncJobUpdate,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
) -> IntegrationSyncJob:
    service = get_integrations_service(db)
    job = service.update_sync_job(job_id, payload.model_dump(exclude_unset=True))
    if job is None:
        raise_not_found("Integration sync job not found")
    db.commit()
    db.refresh(job)
    return job


@router.get("/events", response_model=IntegrationEventListResponse)
def list_events(
    filters: IntegrationEventFilterParams = Depends(),
    service: IntegrationsService = Depends(get_integrations_service),
    _: User = Depends(get_current_user),
) -> IntegrationEventListResponse:
    filter_values = filters.model_dump()
    items = service.list_events(**filter_values)
    total = service.count_events(
        **{
            key: value
            for key, value in filter_values.items()
            if key not in {"limit", "offset"}
        },
    )
    return IntegrationEventListResponse(
        items=items,
        total=total,
        limit=filters.limit,
        offset=filters.offset,
    )


@router.post(
    "/events",
    response_model=IntegrationEventResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_event(
    payload: IntegrationEventCreate,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
) -> IntegrationEvent:
    service = get_integrations_service(db)
    event = service.create_event(payload.model_dump())
    db.commit()
    db.refresh(event)
    return event


@router.get(
    "/events/uuid/{event_uuid}",
    response_model=IntegrationEventResponse,
)
def get_event_by_uuid(
    event_uuid: UUID,
    service: IntegrationsService = Depends(get_integrations_service),
    _: User = Depends(get_current_user),
) -> IntegrationEvent:
    event = service.get_event_by_uuid(event_uuid)
    if event is None:
        raise_not_found("Integration event not found")
    return event


@router.get("/events/{event_id}", response_model=IntegrationEventResponse)
def get_event(
    event_id: int,
    service: IntegrationsService = Depends(get_integrations_service),
    _: User = Depends(get_current_user),
) -> IntegrationEvent:
    event = service.get_event(event_id)
    if event is None:
        raise_not_found("Integration event not found")
    return event


@router.patch("/events/{event_id}", response_model=IntegrationEventResponse)
def update_event(
    event_id: int,
    payload: IntegrationEventUpdate,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
) -> IntegrationEvent:
    service = get_integrations_service(db)
    event = service.update_event(event_id, payload.model_dump(exclude_unset=True))
    if event is None:
        raise_not_found("Integration event not found")
    db.commit()
    db.refresh(event)
    return event
