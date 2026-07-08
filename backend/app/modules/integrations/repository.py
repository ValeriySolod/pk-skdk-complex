"""Repository operations for the Integrations module."""

from __future__ import annotations

from collections.abc import Mapping
from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import Select, func, select
from sqlalchemy.orm import Session

from app.modules.integrations.models import (
    IntegrationConnection,
    IntegrationConnectionStatus,
    IntegrationEvent,
    IntegrationProvider,
    IntegrationProviderStatus,
    IntegrationSyncJob,
)


class IntegrationProviderRepository:
    """Persistence operations for external integration provider definitions."""

    _mutable_fields = frozenset(
        {
            "code",
            "name",
            "description",
            "provider_type",
            "status",
            "auth_type",
            "base_url",
            "capabilities",
            "default_config",
            "metadata_json",
        },
    )

    def __init__(self, db: Session) -> None:
        self.db = db

    def create(self, provider: IntegrationProvider) -> IntegrationProvider:
        self.db.add(provider)
        self.db.flush()
        return provider

    def create_provider(self, provider: IntegrationProvider) -> IntegrationProvider:
        return self.create(provider)

    def get_by_id(
        self,
        provider_id: int,
        *,
        include_deleted: bool = False,
    ) -> IntegrationProvider | None:
        provider = self.db.get(IntegrationProvider, provider_id)
        if (
            provider is not None
            and provider.deleted_at is not None
            and not include_deleted
        ):
            return None
        return provider

    def get_by_uuid(
        self,
        provider_uuid: UUID,
        *,
        include_deleted: bool = False,
    ) -> IntegrationProvider | None:
        query = select(IntegrationProvider).where(
            IntegrationProvider.provider_uuid == provider_uuid,
        )
        if not include_deleted:
            query = query.where(IntegrationProvider.deleted_at.is_(None))
        return self.db.scalar(query)

    def get_by_code(
        self,
        code: str,
        *,
        include_deleted: bool = False,
    ) -> IntegrationProvider | None:
        query = select(IntegrationProvider).where(IntegrationProvider.code == code)
        if not include_deleted:
            query = query.where(IntegrationProvider.deleted_at.is_(None))
        return self.db.scalar(query)

    def list(
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
        query = self._build_query(
            code=code,
            provider_type=provider_type,
            status=status,
            auth_type=auth_type,
            created_from=created_from,
            created_to=created_to,
            include_deleted=include_deleted,
        ).order_by(IntegrationProvider.created_at.desc(), IntegrationProvider.id.desc())

        if offset is not None:
            query = query.offset(offset)
        if limit is not None:
            query = query.limit(limit)

        return list(self.db.scalars(query).all())

    def count(
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
        query = self._build_query(
            code=code,
            provider_type=provider_type,
            status=status,
            auth_type=auth_type,
            created_from=created_from,
            created_to=created_to,
            include_deleted=include_deleted,
        )
        return self.db.scalar(select(func.count()).select_from(query.subquery())) or 0

    def update(
        self,
        provider_id: int,
        values: Mapping[str, object],
    ) -> IntegrationProvider | None:
        provider = self.get_by_id(provider_id)
        if provider is None:
            return None

        unsupported_fields = set(values) - self._mutable_fields
        if unsupported_fields:
            fields = ", ".join(sorted(unsupported_fields))
            raise ValueError(f"Unsupported integration provider update fields: {fields}")

        for field, value in values.items():
            setattr(provider, field, value)

        self.db.flush()
        return provider

    def delete(self, provider_id: int) -> bool:
        provider = self.get_by_id(provider_id)
        if provider is None:
            return False

        provider.status = IntegrationProviderStatus.ARCHIVED.value
        provider.deleted_at = datetime.now(timezone.utc)
        self.db.flush()
        return True

    def mark_deleted(self, provider_id: int) -> bool:
        return self.delete(provider_id)

    def exists(self, provider_id: int, *, include_deleted: bool = False) -> bool:
        return self.get_by_id(provider_id, include_deleted=include_deleted) is not None

    def health(self) -> bool:
        return self.db.scalar(select(1)) == 1

    def _build_query(
        self,
        *,
        code: str | None = None,
        provider_type: str | None = None,
        status: str | None = None,
        auth_type: str | None = None,
        created_from: datetime | None = None,
        created_to: datetime | None = None,
        include_deleted: bool = False,
    ) -> Select[tuple[IntegrationProvider]]:
        query = select(IntegrationProvider)

        if not include_deleted:
            query = query.where(IntegrationProvider.deleted_at.is_(None))
        if code is not None:
            query = query.where(IntegrationProvider.code == code)
        if provider_type is not None:
            query = query.where(IntegrationProvider.provider_type == provider_type)
        if status is not None:
            query = query.where(IntegrationProvider.status == status)
        if auth_type is not None:
            query = query.where(IntegrationProvider.auth_type == auth_type)
        if created_from is not None:
            query = query.where(IntegrationProvider.created_at >= created_from)
        if created_to is not None:
            query = query.where(IntegrationProvider.created_at <= created_to)

        return query


class IntegrationConnectionRepository:
    """Persistence operations for configured integration connections."""

    _mutable_fields = frozenset(
        {
            "provider_id",
            "name",
            "description",
            "status",
            "environment",
            "external_account_id",
            "config",
            "credentials_ref",
            "sync_settings",
            "metadata_json",
            "last_sync_at",
            "last_error_at",
            "last_error_message",
            "updated_by_id",
            "deleted_by_id",
        },
    )

    def __init__(self, db: Session) -> None:
        self.db = db

    def create(self, connection: IntegrationConnection) -> IntegrationConnection:
        self.db.add(connection)
        self.db.flush()
        return connection

    def create_connection(
        self,
        connection: IntegrationConnection,
    ) -> IntegrationConnection:
        return self.create(connection)

    def get_by_id(
        self,
        connection_id: int,
        *,
        include_deleted: bool = False,
    ) -> IntegrationConnection | None:
        connection = self.db.get(IntegrationConnection, connection_id)
        if (
            connection is not None
            and connection.deleted_at is not None
            and not include_deleted
        ):
            return None
        return connection

    def get_by_uuid(
        self,
        connection_uuid: UUID,
        *,
        include_deleted: bool = False,
    ) -> IntegrationConnection | None:
        query = select(IntegrationConnection).where(
            IntegrationConnection.connection_uuid == connection_uuid,
        )
        if not include_deleted:
            query = query.where(IntegrationConnection.deleted_at.is_(None))
        return self.db.scalar(query)

    def get_by_provider_name(
        self,
        provider_id: int,
        name: str,
        *,
        include_deleted: bool = False,
    ) -> IntegrationConnection | None:
        query = select(IntegrationConnection).where(
            IntegrationConnection.provider_id == provider_id,
            IntegrationConnection.name == name,
        )
        if not include_deleted:
            query = query.where(IntegrationConnection.deleted_at.is_(None))
        return self.db.scalar(query)

    def list(
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
        query = self._build_query(
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
        ).order_by(
            IntegrationConnection.created_at.desc(),
            IntegrationConnection.id.desc(),
        )

        if offset is not None:
            query = query.offset(offset)
        if limit is not None:
            query = query.limit(limit)

        return list(self.db.scalars(query).all())

    def count(
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
        query = self._build_query(
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
        return self.db.scalar(select(func.count()).select_from(query.subquery())) or 0

    def update(
        self,
        connection_id: int,
        values: Mapping[str, object],
    ) -> IntegrationConnection | None:
        connection = self.get_by_id(connection_id)
        if connection is None:
            return None

        unsupported_fields = set(values) - self._mutable_fields
        if unsupported_fields:
            fields = ", ".join(sorted(unsupported_fields))
            raise ValueError(f"Unsupported integration connection update fields: {fields}")

        for field, value in values.items():
            setattr(connection, field, value)

        self.db.flush()
        return connection

    def delete(self, connection_id: int, *, deleted_by_id: int | None = None) -> bool:
        connection = self.get_by_id(connection_id)
        if connection is None:
            return False

        connection.status = IntegrationConnectionStatus.ARCHIVED.value
        connection.deleted_at = datetime.now(timezone.utc)
        if deleted_by_id is not None:
            connection.deleted_by_id = deleted_by_id
        self.db.flush()
        return True

    def mark_deleted(
        self,
        connection_id: int,
        *,
        deleted_by_id: int | None = None,
    ) -> bool:
        return self.delete(connection_id, deleted_by_id=deleted_by_id)

    def exists(self, connection_id: int, *, include_deleted: bool = False) -> bool:
        return self.get_by_id(connection_id, include_deleted=include_deleted) is not None

    def health(self) -> bool:
        return self.db.scalar(select(1)) == 1

    def _build_query(
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
    ) -> Select[tuple[IntegrationConnection]]:
        query = select(IntegrationConnection)

        if not include_deleted:
            query = query.where(IntegrationConnection.deleted_at.is_(None))
        if provider_id is not None:
            query = query.where(IntegrationConnection.provider_id == provider_id)
        if name is not None:
            query = query.where(IntegrationConnection.name == name)
        if status is not None:
            query = query.where(IntegrationConnection.status == status)
        if environment is not None:
            query = query.where(IntegrationConnection.environment == environment)
        if external_account_id is not None:
            query = query.where(
                IntegrationConnection.external_account_id == external_account_id,
            )
        if created_by_id is not None:
            query = query.where(IntegrationConnection.created_by_id == created_by_id)
        if updated_by_id is not None:
            query = query.where(IntegrationConnection.updated_by_id == updated_by_id)
        if last_sync_from is not None:
            query = query.where(IntegrationConnection.last_sync_at >= last_sync_from)
        if last_sync_to is not None:
            query = query.where(IntegrationConnection.last_sync_at <= last_sync_to)
        if created_from is not None:
            query = query.where(IntegrationConnection.created_at >= created_from)
        if created_to is not None:
            query = query.where(IntegrationConnection.created_at <= created_to)

        return query


class IntegrationSyncJobRepository:
    """Persistence operations for integration synchronization jobs."""

    _mutable_fields = frozenset(
        {
            "sync_type",
            "direction",
            "status",
            "request_payload",
            "result_summary",
            "records_processed",
            "records_succeeded",
            "records_failed",
            "scheduled_at",
            "started_at",
            "completed_at",
            "failed_at",
            "failure_reason",
            "correlation_id",
            "metadata_json",
        },
    )

    def __init__(self, db: Session) -> None:
        self.db = db

    def create(self, job: IntegrationSyncJob) -> IntegrationSyncJob:
        self.db.add(job)
        self.db.flush()
        return job

    def create_sync_job(self, job: IntegrationSyncJob) -> IntegrationSyncJob:
        return self.create(job)

    def get_by_id(self, job_id: int) -> IntegrationSyncJob | None:
        return self.db.get(IntegrationSyncJob, job_id)

    def get_by_uuid(self, job_uuid: UUID) -> IntegrationSyncJob | None:
        return self.db.scalar(
            select(IntegrationSyncJob).where(
                IntegrationSyncJob.job_uuid == job_uuid,
            ),
        )

    def list(
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
        query = self._build_query(
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
        ).order_by(IntegrationSyncJob.created_at.desc(), IntegrationSyncJob.id.desc())

        if offset is not None:
            query = query.offset(offset)
        if limit is not None:
            query = query.limit(limit)

        return list(self.db.scalars(query).all())

    def count(
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
        query = self._build_query(
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
        return self.db.scalar(select(func.count()).select_from(query.subquery())) or 0

    def update(
        self,
        job_id: int,
        values: Mapping[str, object],
    ) -> IntegrationSyncJob | None:
        job = self.get_by_id(job_id)
        if job is None:
            return None

        unsupported_fields = set(values) - self._mutable_fields
        if unsupported_fields:
            fields = ", ".join(sorted(unsupported_fields))
            raise ValueError(f"Unsupported integration sync job update fields: {fields}")

        for field, value in values.items():
            setattr(job, field, value)

        self.db.flush()
        return job

    def exists(self, job_id: int) -> bool:
        return self.get_by_id(job_id) is not None

    def health(self) -> bool:
        return self.db.scalar(select(1)) == 1

    def _build_query(
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
    ) -> Select[tuple[IntegrationSyncJob]]:
        query = select(IntegrationSyncJob)

        if connection_id is not None:
            query = query.where(IntegrationSyncJob.connection_id == connection_id)
        if sync_type is not None:
            query = query.where(IntegrationSyncJob.sync_type == sync_type)
        if direction is not None:
            query = query.where(IntegrationSyncJob.direction == direction)
        if status is not None:
            query = query.where(IntegrationSyncJob.status == status)
        if triggered_by_user_id is not None:
            query = query.where(
                IntegrationSyncJob.triggered_by_user_id == triggered_by_user_id,
            )
        if correlation_id is not None:
            query = query.where(IntegrationSyncJob.correlation_id == correlation_id)
        if scheduled_from is not None:
            query = query.where(IntegrationSyncJob.scheduled_at >= scheduled_from)
        if scheduled_to is not None:
            query = query.where(IntegrationSyncJob.scheduled_at <= scheduled_to)
        if started_from is not None:
            query = query.where(IntegrationSyncJob.started_at >= started_from)
        if started_to is not None:
            query = query.where(IntegrationSyncJob.started_at <= started_to)
        if completed_from is not None:
            query = query.where(IntegrationSyncJob.completed_at >= completed_from)
        if completed_to is not None:
            query = query.where(IntegrationSyncJob.completed_at <= completed_to)
        if created_from is not None:
            query = query.where(IntegrationSyncJob.created_at >= created_from)
        if created_to is not None:
            query = query.where(IntegrationSyncJob.created_at <= created_to)

        return query


class IntegrationEventRepository:
    """Persistence operations for integration event records."""

    _mutable_fields = frozenset(
        {
            "status",
            "payload",
            "headers",
            "processing_result",
            "error_message",
            "processed_at",
            "correlation_id",
            "metadata_json",
        },
    )

    def __init__(self, db: Session) -> None:
        self.db = db

    def create(self, event: IntegrationEvent) -> IntegrationEvent:
        self.db.add(event)
        self.db.flush()
        return event

    def create_event(self, event: IntegrationEvent) -> IntegrationEvent:
        return self.create(event)

    def get_by_id(self, event_id: int) -> IntegrationEvent | None:
        return self.db.get(IntegrationEvent, event_id)

    def get_by_uuid(self, event_uuid: UUID) -> IntegrationEvent | None:
        return self.db.scalar(
            select(IntegrationEvent).where(IntegrationEvent.event_uuid == event_uuid),
        )

    def get_by_external_event_id(
        self,
        external_event_id: str,
    ) -> IntegrationEvent | None:
        return self.db.scalar(
            select(IntegrationEvent).where(
                IntegrationEvent.external_event_id == external_event_id,
            ),
        )

    def list(
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
        query = self._build_query(
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
        ).order_by(IntegrationEvent.received_at.desc(), IntegrationEvent.id.desc())

        if offset is not None:
            query = query.offset(offset)
        if limit is not None:
            query = query.limit(limit)

        return list(self.db.scalars(query).all())

    def count(
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
        query = self._build_query(
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
        return self.db.scalar(select(func.count()).select_from(query.subquery())) or 0

    def update(
        self,
        event_id: int,
        values: Mapping[str, object],
    ) -> IntegrationEvent | None:
        event = self.get_by_id(event_id)
        if event is None:
            return None

        unsupported_fields = set(values) - self._mutable_fields
        if unsupported_fields:
            fields = ", ".join(sorted(unsupported_fields))
            raise ValueError(f"Unsupported integration event update fields: {fields}")

        for field, value in values.items():
            setattr(event, field, value)

        self.db.flush()
        return event

    def exists(self, event_id: int) -> bool:
        return self.get_by_id(event_id) is not None

    def health(self) -> bool:
        return self.db.scalar(select(1)) == 1

    def _build_query(
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
    ) -> Select[tuple[IntegrationEvent]]:
        query = select(IntegrationEvent)

        if connection_id is not None:
            query = query.where(IntegrationEvent.connection_id == connection_id)
        if sync_job_id is not None:
            query = query.where(IntegrationEvent.sync_job_id == sync_job_id)
        if event_type is not None:
            query = query.where(IntegrationEvent.event_type == event_type)
        if status is not None:
            query = query.where(IntegrationEvent.status == status)
        if source is not None:
            query = query.where(IntegrationEvent.source == source)
        if external_event_id is not None:
            query = query.where(
                IntegrationEvent.external_event_id == external_event_id,
            )
        if entity_type is not None:
            query = query.where(IntegrationEvent.entity_type == entity_type)
        if entity_id is not None:
            query = query.where(IntegrationEvent.entity_id == entity_id)
        if correlation_id is not None:
            query = query.where(IntegrationEvent.correlation_id == correlation_id)
        if received_from is not None:
            query = query.where(IntegrationEvent.received_at >= received_from)
        if received_to is not None:
            query = query.where(IntegrationEvent.received_at <= received_to)
        if processed_from is not None:
            query = query.where(IntegrationEvent.processed_at >= processed_from)
        if processed_to is not None:
            query = query.where(IntegrationEvent.processed_at <= processed_to)
        if created_from is not None:
            query = query.where(IntegrationEvent.created_at >= created_from)
        if created_to is not None:
            query = query.where(IntegrationEvent.created_at <= created_to)

        return query


class IntegrationsRepository:
    """Persistence boundary for integrations data."""

    def __init__(self, db: Session) -> None:
        self.db = db
        self.providers = IntegrationProviderRepository(db)
        self.connections = IntegrationConnectionRepository(db)
        self.sync_jobs = IntegrationSyncJobRepository(db)
        self.events = IntegrationEventRepository(db)

    def health(self) -> bool:
        """Return whether all integration persistence boundaries are available."""
        return (
            self.providers.health()
            and self.connections.health()
            and self.sync_jobs.health()
            and self.events.health()
        )

    def health_check(self) -> bool:
        return self.health()


__all__ = [
    "IntegrationConnectionRepository",
    "IntegrationEventRepository",
    "IntegrationProviderRepository",
    "IntegrationSyncJobRepository",
    "IntegrationsRepository",
]
