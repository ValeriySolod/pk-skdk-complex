"""Service layer for the Integrations module."""

from __future__ import annotations

from collections.abc import Mapping
from datetime import datetime
from typing import Any
from uuid import UUID

from app.modules.integrations.models import (
    IntegrationConnection,
    IntegrationEvent,
    IntegrationProvider,
    IntegrationSyncJob,
)
from app.modules.integrations.repository import IntegrationsRepository
from app.modules.integrations.schemas import IntegrationsHealthRead

Payload = Mapping[str, Any]


class IntegrationsService:
    """Business boundary for external service connection workflows."""

    def __init__(self, repository: IntegrationsRepository) -> None:
        self.repository = repository
        self.providers = repository.providers
        self.connections = repository.connections
        self.sync_jobs = repository.sync_jobs
        self.events = repository.events

    def health(self) -> IntegrationsHealthRead:
        """Return aggregate Integrations module health."""

        return IntegrationsHealthRead(
            module="integrations",
            status="ok" if self.repository.health() else "error",
        )

    # Providers

    def create_provider(
        self,
        payload: Payload | IntegrationProvider,
    ) -> IntegrationProvider:
        """Create an integration provider definition."""

        provider = (
            payload
            if isinstance(payload, IntegrationProvider)
            else IntegrationProvider(**dict(payload))
        )
        return self.providers.create_provider(provider)

    def get_provider(
        self,
        provider_id: int,
        *,
        include_deleted: bool = False,
    ) -> IntegrationProvider | None:
        """Get an integration provider by integer ID."""

        return self.providers.get_by_id(provider_id, include_deleted=include_deleted)

    def get_provider_by_id(
        self,
        provider_id: int,
        *,
        include_deleted: bool = False,
    ) -> IntegrationProvider | None:
        """Get an integration provider by integer ID."""

        return self.get_provider(provider_id, include_deleted=include_deleted)

    def get_provider_by_uuid(
        self,
        provider_uuid: UUID,
        *,
        include_deleted: bool = False,
    ) -> IntegrationProvider | None:
        """Get an integration provider by UUID."""

        return self.providers.get_by_uuid(
            provider_uuid,
            include_deleted=include_deleted,
        )

    def get_provider_by_code(
        self,
        code: str,
        *,
        include_deleted: bool = False,
    ) -> IntegrationProvider | None:
        """Get an integration provider by stable code."""

        return self.providers.get_by_code(code, include_deleted=include_deleted)

    def list_providers(
        self,
        *,
        code: str | None = None,
        provider_type: str | None = None,
        status: str | None = None,
        auth_type: str | None = None,
        created_from: datetime | None = None,
        created_to: datetime | None = None,
        include_deleted: bool = False,
        limit: int | None = None,
        offset: int | None = None,
    ) -> list[IntegrationProvider]:
        """List integration providers using repository filters."""

        return self.providers.list(
            code=code,
            provider_type=provider_type,
            status=status,
            auth_type=auth_type,
            created_from=created_from,
            created_to=created_to,
            include_deleted=include_deleted,
            limit=limit,
            offset=offset,
        )

    def count_providers(
        self,
        *,
        code: str | None = None,
        provider_type: str | None = None,
        status: str | None = None,
        auth_type: str | None = None,
        created_from: datetime | None = None,
        created_to: datetime | None = None,
        include_deleted: bool = False,
    ) -> int:
        """Count integration providers using repository filters."""

        return self.providers.count(
            code=code,
            provider_type=provider_type,
            status=status,
            auth_type=auth_type,
            created_from=created_from,
            created_to=created_to,
            include_deleted=include_deleted,
        )

    def update_provider(
        self,
        provider_id: int,
        values: Payload,
    ) -> IntegrationProvider | None:
        """Update mutable integration provider fields."""

        return self.providers.update(provider_id, values)

    def delete_provider(self, provider_id: int) -> bool:
        """Soft-delete an integration provider."""

        return self.providers.delete(provider_id)

    def mark_provider_deleted(self, provider_id: int) -> bool:
        """Soft-delete an integration provider using lifecycle alias."""

        return self.providers.mark_deleted(provider_id)

    def provider_exists(
        self,
        provider_id: int,
        *,
        include_deleted: bool = False,
    ) -> bool:
        """Return whether an integration provider exists."""

        return self.providers.exists(provider_id, include_deleted=include_deleted)

    # Connections

    def create_connection(
        self,
        payload: Payload | IntegrationConnection,
    ) -> IntegrationConnection:
        """Create an integration connection."""

        connection = (
            payload
            if isinstance(payload, IntegrationConnection)
            else IntegrationConnection(**dict(payload))
        )
        return self.connections.create_connection(connection)

    def get_connection(
        self,
        connection_id: int,
        *,
        include_deleted: bool = False,
    ) -> IntegrationConnection | None:
        """Get an integration connection by integer ID."""

        return self.connections.get_by_id(
            connection_id,
            include_deleted=include_deleted,
        )

    def get_connection_by_id(
        self,
        connection_id: int,
        *,
        include_deleted: bool = False,
    ) -> IntegrationConnection | None:
        """Get an integration connection by integer ID."""

        return self.get_connection(connection_id, include_deleted=include_deleted)

    def get_connection_by_uuid(
        self,
        connection_uuid: UUID,
        *,
        include_deleted: bool = False,
    ) -> IntegrationConnection | None:
        """Get an integration connection by UUID."""

        return self.connections.get_by_uuid(
            connection_uuid,
            include_deleted=include_deleted,
        )

    def get_connection_by_provider_name(
        self,
        provider_id: int,
        name: str,
        *,
        include_deleted: bool = False,
    ) -> IntegrationConnection | None:
        """Get an integration connection by provider and name."""

        return self.connections.get_by_provider_name(
            provider_id,
            name,
            include_deleted=include_deleted,
        )

    def list_connections(
        self,
        *,
        provider_id: int | None = None,
        name: str | None = None,
        status: str | None = None,
        environment: str | None = None,
        external_account_id: str | None = None,
        created_by_id: int | None = None,
        updated_by_id: int | None = None,
        last_sync_from: datetime | None = None,
        last_sync_to: datetime | None = None,
        created_from: datetime | None = None,
        created_to: datetime | None = None,
        include_deleted: bool = False,
        limit: int | None = None,
        offset: int | None = None,
    ) -> list[IntegrationConnection]:
        """List integration connections using repository filters."""

        return self.connections.list(
            provider_id=provider_id,
            name=name,
            status=status,
            environment=environment,
            external_account_id=external_account_id,
            created_by_id=created_by_id,
            updated_by_id=updated_by_id,
            last_sync_from=last_sync_from,
            last_sync_to=last_sync_to,
            created_from=created_from,
            created_to=created_to,
            include_deleted=include_deleted,
            limit=limit,
            offset=offset,
        )

    def count_connections(
        self,
        *,
        provider_id: int | None = None,
        name: str | None = None,
        status: str | None = None,
        environment: str | None = None,
        external_account_id: str | None = None,
        created_by_id: int | None = None,
        updated_by_id: int | None = None,
        last_sync_from: datetime | None = None,
        last_sync_to: datetime | None = None,
        created_from: datetime | None = None,
        created_to: datetime | None = None,
        include_deleted: bool = False,
    ) -> int:
        """Count integration connections using repository filters."""

        return self.connections.count(
            provider_id=provider_id,
            name=name,
            status=status,
            environment=environment,
            external_account_id=external_account_id,
            created_by_id=created_by_id,
            updated_by_id=updated_by_id,
            last_sync_from=last_sync_from,
            last_sync_to=last_sync_to,
            created_from=created_from,
            created_to=created_to,
            include_deleted=include_deleted,
        )

    def update_connection(
        self,
        connection_id: int,
        values: Payload,
    ) -> IntegrationConnection | None:
        """Update mutable integration connection fields."""

        return self.connections.update(connection_id, values)

    def delete_connection(
        self,
        connection_id: int,
        *,
        deleted_by_id: int | None = None,
    ) -> bool:
        """Soft-delete an integration connection."""

        return self.connections.delete(connection_id, deleted_by_id=deleted_by_id)

    def mark_connection_deleted(
        self,
        connection_id: int,
        *,
        deleted_by_id: int | None = None,
    ) -> bool:
        """Soft-delete an integration connection using lifecycle alias."""

        return self.connections.mark_deleted(
            connection_id,
            deleted_by_id=deleted_by_id,
        )

    def connection_exists(
        self,
        connection_id: int,
        *,
        include_deleted: bool = False,
    ) -> bool:
        """Return whether an integration connection exists."""

        return self.connections.exists(
            connection_id,
            include_deleted=include_deleted,
        )

    # Sync jobs

    def create_sync_job(
        self,
        payload: Payload | IntegrationSyncJob,
    ) -> IntegrationSyncJob:
        """Create an integration synchronization job."""

        job = (
            payload
            if isinstance(payload, IntegrationSyncJob)
            else IntegrationSyncJob(**dict(payload))
        )
        return self.sync_jobs.create_sync_job(job)

    def get_sync_job(self, job_id: int) -> IntegrationSyncJob | None:
        """Get an integration synchronization job by integer ID."""

        return self.sync_jobs.get_by_id(job_id)

    def get_sync_job_by_id(self, job_id: int) -> IntegrationSyncJob | None:
        """Get an integration synchronization job by integer ID."""

        return self.get_sync_job(job_id)

    def get_sync_job_by_uuid(self, job_uuid: UUID) -> IntegrationSyncJob | None:
        """Get an integration synchronization job by UUID."""

        return self.sync_jobs.get_by_uuid(job_uuid)

    def list_sync_jobs(
        self,
        *,
        connection_id: int | None = None,
        sync_type: str | None = None,
        direction: str | None = None,
        status: str | None = None,
        triggered_by_user_id: int | None = None,
        correlation_id: str | None = None,
        scheduled_from: datetime | None = None,
        scheduled_to: datetime | None = None,
        started_from: datetime | None = None,
        started_to: datetime | None = None,
        completed_from: datetime | None = None,
        completed_to: datetime | None = None,
        created_from: datetime | None = None,
        created_to: datetime | None = None,
        limit: int | None = None,
        offset: int | None = None,
    ) -> list[IntegrationSyncJob]:
        """List integration synchronization jobs using repository filters."""

        return self.sync_jobs.list(
            connection_id=connection_id,
            sync_type=sync_type,
            direction=direction,
            status=status,
            triggered_by_user_id=triggered_by_user_id,
            correlation_id=correlation_id,
            scheduled_from=scheduled_from,
            scheduled_to=scheduled_to,
            started_from=started_from,
            started_to=started_to,
            completed_from=completed_from,
            completed_to=completed_to,
            created_from=created_from,
            created_to=created_to,
            limit=limit,
            offset=offset,
        )

    def count_sync_jobs(
        self,
        *,
        connection_id: int | None = None,
        sync_type: str | None = None,
        direction: str | None = None,
        status: str | None = None,
        triggered_by_user_id: int | None = None,
        correlation_id: str | None = None,
        scheduled_from: datetime | None = None,
        scheduled_to: datetime | None = None,
        started_from: datetime | None = None,
        started_to: datetime | None = None,
        completed_from: datetime | None = None,
        completed_to: datetime | None = None,
        created_from: datetime | None = None,
        created_to: datetime | None = None,
    ) -> int:
        """Count integration synchronization jobs using repository filters."""

        return self.sync_jobs.count(
            connection_id=connection_id,
            sync_type=sync_type,
            direction=direction,
            status=status,
            triggered_by_user_id=triggered_by_user_id,
            correlation_id=correlation_id,
            scheduled_from=scheduled_from,
            scheduled_to=scheduled_to,
            started_from=started_from,
            started_to=started_to,
            completed_from=completed_from,
            completed_to=completed_to,
            created_from=created_from,
            created_to=created_to,
        )

    def update_sync_job(
        self,
        job_id: int,
        values: Payload,
    ) -> IntegrationSyncJob | None:
        """Update mutable integration synchronization job fields."""

        return self.sync_jobs.update(job_id, values)

    def sync_job_exists(self, job_id: int) -> bool:
        """Return whether an integration synchronization job exists."""

        return self.sync_jobs.exists(job_id)

    # Events

    def create_event(self, payload: Payload | IntegrationEvent) -> IntegrationEvent:
        """Create an integration event."""

        event = (
            payload
            if isinstance(payload, IntegrationEvent)
            else IntegrationEvent(**dict(payload))
        )
        return self.events.create_event(event)

    def get_event(self, event_id: int) -> IntegrationEvent | None:
        """Get an integration event by integer ID."""

        return self.events.get_by_id(event_id)

    def get_event_by_id(self, event_id: int) -> IntegrationEvent | None:
        """Get an integration event by integer ID."""

        return self.get_event(event_id)

    def get_event_by_uuid(self, event_uuid: UUID) -> IntegrationEvent | None:
        """Get an integration event by UUID."""

        return self.events.get_by_uuid(event_uuid)

    def get_event_by_external_event_id(
        self,
        external_event_id: str,
    ) -> IntegrationEvent | None:
        """Get an integration event by upstream event identifier."""

        return self.events.get_by_external_event_id(external_event_id)

    def list_events(
        self,
        *,
        connection_id: int | None = None,
        sync_job_id: int | None = None,
        event_type: str | None = None,
        status: str | None = None,
        source: str | None = None,
        external_event_id: str | None = None,
        entity_type: str | None = None,
        entity_id: str | None = None,
        correlation_id: str | None = None,
        received_from: datetime | None = None,
        received_to: datetime | None = None,
        processed_from: datetime | None = None,
        processed_to: datetime | None = None,
        created_from: datetime | None = None,
        created_to: datetime | None = None,
        limit: int | None = None,
        offset: int | None = None,
    ) -> list[IntegrationEvent]:
        """List integration events using repository filters."""

        return self.events.list(
            connection_id=connection_id,
            sync_job_id=sync_job_id,
            event_type=event_type,
            status=status,
            source=source,
            external_event_id=external_event_id,
            entity_type=entity_type,
            entity_id=entity_id,
            correlation_id=correlation_id,
            received_from=received_from,
            received_to=received_to,
            processed_from=processed_from,
            processed_to=processed_to,
            created_from=created_from,
            created_to=created_to,
            limit=limit,
            offset=offset,
        )

    def count_events(
        self,
        *,
        connection_id: int | None = None,
        sync_job_id: int | None = None,
        event_type: str | None = None,
        status: str | None = None,
        source: str | None = None,
        external_event_id: str | None = None,
        entity_type: str | None = None,
        entity_id: str | None = None,
        correlation_id: str | None = None,
        received_from: datetime | None = None,
        received_to: datetime | None = None,
        processed_from: datetime | None = None,
        processed_to: datetime | None = None,
        created_from: datetime | None = None,
        created_to: datetime | None = None,
    ) -> int:
        """Count integration events using repository filters."""

        return self.events.count(
            connection_id=connection_id,
            sync_job_id=sync_job_id,
            event_type=event_type,
            status=status,
            source=source,
            external_event_id=external_event_id,
            entity_type=entity_type,
            entity_id=entity_id,
            correlation_id=correlation_id,
            received_from=received_from,
            received_to=received_to,
            processed_from=processed_from,
            processed_to=processed_to,
            created_from=created_from,
            created_to=created_to,
        )

    def update_event(
        self,
        event_id: int,
        values: Payload,
    ) -> IntegrationEvent | None:
        """Update mutable integration event fields."""

        return self.events.update(event_id, values)

    def event_exists(self, event_id: int) -> bool:
        """Return whether an integration event exists."""

        return self.events.exists(event_id)

    # Compatibility aliases
    create = create_provider
    get_by_id = get_provider_by_id
    get_by_uuid = get_provider_by_uuid
    list = list_providers
    count = count_providers
    update = update_provider
    delete = delete_provider
    mark_deleted = mark_provider_deleted
    exists = provider_exists

    create_integration_provider = create_provider
    get_integration_provider = get_provider
    get_integration_provider_by_id = get_provider_by_id
    get_integration_provider_by_uuid = get_provider_by_uuid
    get_integration_provider_by_code = get_provider_by_code
    list_integration_providers = list_providers
    count_integration_providers = count_providers
    update_integration_provider = update_provider
    delete_integration_provider = delete_provider
    mark_integration_provider_deleted = mark_provider_deleted
    integration_provider_exists = provider_exists

    create_integration_connection = create_connection
    get_integration_connection = get_connection
    get_integration_connection_by_id = get_connection_by_id
    get_integration_connection_by_uuid = get_connection_by_uuid
    list_integration_connections = list_connections
    count_integration_connections = count_connections
    update_integration_connection = update_connection
    delete_integration_connection = delete_connection
    mark_integration_connection_deleted = mark_connection_deleted
    integration_connection_exists = connection_exists

    create_job = create_sync_job
    get_job = get_sync_job
    get_job_by_id = get_sync_job_by_id
    get_job_by_uuid = get_sync_job_by_uuid
    list_jobs = list_sync_jobs
    count_jobs = count_sync_jobs
    update_job = update_sync_job
    job_exists = sync_job_exists

    create_integration_event = create_event
    get_integration_event = get_event
    get_integration_event_by_id = get_event_by_id
    get_integration_event_by_uuid = get_event_by_uuid
    list_integration_events = list_events
    count_integration_events = count_events
    update_integration_event = update_event
    integration_event_exists = event_exists


__all__ = ["IntegrationsService"]
