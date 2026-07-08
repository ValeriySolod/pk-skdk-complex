from __future__ import annotations

from datetime import datetime
from uuid import uuid4

import pytest
from sqlalchemy.orm import Session

from app.modules.integrations.models import (
    IntegrationConnectionStatus,
    IntegrationEventStatus,
    IntegrationProvider,
    IntegrationProviderStatus,
    IntegrationSyncJobStatus,
)
from app.modules.integrations.repository import (
    IntegrationConnectionRepository,
    IntegrationEventRepository,
    IntegrationProviderRepository,
    IntegrationSyncJobRepository,
    IntegrationsRepository,
)
from app.modules.integrations.service import IntegrationsService


@pytest.fixture()
def service(db_session: Session) -> IntegrationsService:
    return IntegrationsService(IntegrationsRepository(db_session))


def create_provider(
    service: IntegrationsService,
    *,
    code: str = "email-gateway",
    name: str = "Email Gateway",
    provider_type: str = "email",
    status: str = IntegrationProviderStatus.ACTIVE.value,
    auth_type: str | None = "api_key",
    created_at: datetime | None = None,
) -> IntegrationProvider:
    return service.create_provider(
        {
            "code": code,
            "name": name,
            "description": "Outbound email provider",
            "provider_type": provider_type,
            "status": status,
            "auth_type": auth_type,
            "base_url": "https://integrations.example.test",
            "capabilities": {"send": True, "webhooks": ["delivery"]},
            "default_config": {"timeout": 30},
            "metadata_json": {"source": "service-test"},
            "created_at": created_at,
        }
    )


def test_integrations_service_provider_lifecycle_filters_and_aliases(
    service: IntegrationsService,
) -> None:
    first = create_provider(service, created_at=datetime(2026, 7, 5, 9, 0, 0))
    second = create_provider(
        service,
        code="crm-api",
        name="CRM API",
        provider_type="crm",
        status=IntegrationProviderStatus.INACTIVE.value,
        auth_type="oauth2",
        created_at=datetime(2026, 7, 5, 10, 0, 0),
    )
    original_uuid = first.provider_uuid

    assert service.health().model_dump() == {
        "status": "ok",
        "module": "integrations",
    }
    assert service.get_provider(first.id) == first
    assert service.get_provider_by_id(first.id) == first
    assert service.get_provider_by_uuid(original_uuid) == first
    assert service.get_provider_by_code("email-gateway") == first
    assert service.get_by_id(first.id) == first
    assert service.get_by_uuid(original_uuid) == first
    assert service.get_provider(999) is None
    assert service.get_provider_by_uuid(uuid4()) is None
    assert service.provider_exists(first.id) is True
    assert service.exists(first.id) is True

    assert service.list_providers() == [second, first]
    assert service.list(limit=1) == [second]
    assert service.list_providers(offset=1, limit=1) == [first]
    assert service.list_providers(provider_type="crm") == [second]
    assert service.list_providers(status=IntegrationProviderStatus.ACTIVE.value) == [
        first
    ]
    assert service.list_providers(auth_type="oauth2") == [second]
    assert service.list_providers(created_from=datetime(2026, 7, 5, 10, 0, 0)) == [
        second
    ]
    assert service.count_providers() == 2
    assert service.count(provider_type="email") == 1
    assert service.count_providers(code="missing") == 0

    updated = service.update_provider(
        first.id,
        {
            "name": "Email Gateway Updated",
            "metadata_json": {"source": "updated", "nested": {"version": 2}},
        },
    )

    assert updated is first
    assert first.provider_uuid == original_uuid
    assert first.name == "Email Gateway Updated"
    assert first.metadata_json == {"source": "updated", "nested": {"version": 2}}
    assert service.update_provider(999, {"name": "Missing"}) is None
    with pytest.raises(
        ValueError,
        match="Unsupported integration provider update fields: id",
    ):
        service.update_provider(first.id, {"id": 999})

    assert service.mark_provider_deleted(first.id) is True
    assert first.deleted_at is not None
    assert first.status == IntegrationProviderStatus.ARCHIVED.value
    assert service.get_provider(first.id) is None
    assert service.get_provider(first.id, include_deleted=True) == first
    assert service.count_providers() == 1
    assert service.count_providers(include_deleted=True) == 2
    assert service.delete_provider(999) is False


def test_integrations_service_connection_job_and_event_boundaries(
    service: IntegrationsService,
    db_session: Session,
) -> None:
    provider = create_provider(service)
    connection = service.create_connection(
        {
            "provider_id": provider.id,
            "name": "Production email",
            "description": "Production tenant connection",
            "status": IntegrationConnectionStatus.ACTIVE.value,
            "environment": "production",
            "external_account_id": "acct-001",
            "config": {"region": "eu"},
            "credentials_ref": "secret/email/prod",
            "sync_settings": {"interval": "hourly"},
            "metadata_json": {"tenant": "default"},
            "created_at": datetime(2026, 7, 5, 9, 0, 0),
        }
    )
    other_connection = service.create_connection(
        {
            "provider_id": provider.id,
            "name": "Sandbox email",
            "status": IntegrationConnectionStatus.DRAFT.value,
            "environment": "sandbox",
            "created_at": datetime(2026, 7, 5, 10, 0, 0),
        }
    )
    job = service.create_sync_job(
        {
            "connection_id": connection.id,
            "sync_type": "contacts",
            "direction": "outbound",
            "status": IntegrationSyncJobStatus.QUEUED.value,
            "request_payload": {"batch": 1},
            "correlation_id": "corr-sync-001",
            "created_at": datetime(2026, 7, 5, 11, 0, 0),
        }
    )
    event = service.create_event(
        {
            "connection_id": connection.id,
            "sync_job_id": job.id,
            "event_type": "delivery.created",
            "status": IntegrationEventStatus.RECEIVED.value,
            "source": "webhook",
            "external_event_id": "evt-001",
            "entity_type": "message",
            "entity_id": "msg-001",
            "payload": {"delivered": False},
            "headers": {"x-request-id": "req-001"},
            "correlation_id": "corr-sync-001",
            "created_at": datetime(2026, 7, 5, 12, 0, 0),
        }
    )

    assert service.repository.db is db_session
    assert isinstance(service.providers, IntegrationProviderRepository)
    assert isinstance(service.connections, IntegrationConnectionRepository)
    assert isinstance(service.sync_jobs, IntegrationSyncJobRepository)
    assert isinstance(service.events, IntegrationEventRepository)

    assert service.get_connection(connection.id) == connection
    assert service.get_connection_by_uuid(connection.connection_uuid) == connection
    assert service.get_connection_by_provider_name(
        provider.id,
        "Production email",
    ) == connection
    assert service.connection_exists(connection.id) is True
    assert service.list_connections() == [other_connection, connection]
    assert service.list_connections(provider_id=provider.id, environment="production") == [
        connection
    ]
    assert service.count_connections(status=IntegrationConnectionStatus.ACTIVE.value) == 1
    assert service.update_connection(
        connection.id,
        {"last_error_message": "temporary upstream error"},
    ) is connection
    assert connection.last_error_message == "temporary upstream error"

    assert service.get_sync_job(job.id) == job
    assert service.get_sync_job_by_uuid(job.job_uuid) == job
    assert service.get_job_by_id(job.id) == job
    assert service.list_sync_jobs(connection_id=connection.id) == [job]
    assert service.count_sync_jobs(correlation_id="corr-sync-001") == 1
    assert service.update_sync_job(
        job.id,
        {
            "status": IntegrationSyncJobStatus.COMPLETED.value,
            "records_processed": 3,
            "result_summary": {"ok": True},
        },
    ) is job
    assert job.status == IntegrationSyncJobStatus.COMPLETED.value
    assert job.records_processed == 3

    assert service.get_event(event.id) == event
    assert service.get_event_by_uuid(event.event_uuid) == event
    assert service.get_event_by_external_event_id("evt-001") == event
    assert service.get_integration_event_by_id(event.id) == event
    assert service.list_events(connection_id=connection.id) == [event]
    assert service.count_events(event_type="delivery.created") == 1
    assert service.update_event(
        event.id,
        {
            "status": IntegrationEventStatus.PROCESSED.value,
            "processing_result": {"accepted": True},
        },
    ) is event
    assert event.status == IntegrationEventStatus.PROCESSED.value
    assert event.processing_result == {"accepted": True}

    assert service.get_connection(999) is None
    assert service.get_connection_by_uuid(uuid4()) is None
    assert service.get_sync_job(999) is None
    assert service.get_sync_job_by_uuid(uuid4()) is None
    assert service.get_event(999) is None
    assert service.get_event_by_uuid(uuid4()) is None
    assert service.update_connection(999, {"name": "Missing"}) is None
    assert service.update_sync_job(999, {"status": "missing"}) is None
    assert service.update_event(999, {"status": "missing"}) is None

    assert service.mark_connection_deleted(connection.id, deleted_by_id=42) is True
    assert connection.deleted_at is not None
    assert connection.deleted_by_id == 42
    assert connection.status == IntegrationConnectionStatus.ARCHIVED.value
    assert service.get_connection(connection.id) is None
    assert service.get_connection(connection.id, include_deleted=True) == connection
    assert service.count_connections() == 1
    assert service.count_connections(include_deleted=True) == 2
    assert service.delete_connection(999) is False
