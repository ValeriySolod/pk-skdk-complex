"""Repository operations for the Administration module."""

from __future__ import annotations

from collections.abc import Mapping
from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import Select, func, select
from sqlalchemy.orm import Session

from app.modules.administration.models import (
    AdminActionEvent,
    AdministrationReference,
    MaintenanceTask,
)


class AdministrationReferenceRepository:
    """Persistence operations for administrated reference/catalog entries."""

    _mutable_fields = frozenset(
        {
            "catalog",
            "code",
            "title",
            "description",
            "status",
            "metadata_json",
        },
    )

    def __init__(self, db: Session) -> None:
        self.db = db

    def create(self, reference: AdministrationReference) -> AdministrationReference:
        self.db.add(reference)
        self.db.flush()
        return reference

    def create_reference(
        self,
        reference: AdministrationReference,
    ) -> AdministrationReference:
        return self.create(reference)

    def get_by_id(
        self,
        reference_id: int,
        *,
        include_deleted: bool = False,
    ) -> AdministrationReference | None:
        reference = self.db.get(AdministrationReference, reference_id)
        if (
            reference is not None
            and reference.deleted_at is not None
            and not include_deleted
        ):
            return None
        return reference

    def get_by_uuid(
        self,
        reference_uuid: UUID,
        *,
        include_deleted: bool = False,
    ) -> AdministrationReference | None:
        query = select(AdministrationReference).where(
            AdministrationReference.reference_uuid == reference_uuid,
        )
        if not include_deleted:
            query = query.where(AdministrationReference.deleted_at.is_(None))
        return self.db.scalar(query)

    def get_by_code(
        self,
        code: str,
        *,
        include_deleted: bool = False,
    ) -> AdministrationReference | None:
        query = select(AdministrationReference).where(
            AdministrationReference.code == code
        )
        if not include_deleted:
            query = query.where(AdministrationReference.deleted_at.is_(None))
        return self.db.scalar(query)

    def list(
        self,
        *,
        catalog: str | None = None,
        status: str | None = None,
        created_from: datetime | None = None,
        created_to: datetime | None = None,
        include_deleted: bool = False,
        limit: int | None = None,
        offset: int | None = None,
    ) -> list[AdministrationReference]:
        query = self._build_query(
            catalog=catalog,
            status=status,
            created_from=created_from,
            created_to=created_to,
            include_deleted=include_deleted,
        ).order_by(
            AdministrationReference.created_at.desc(), AdministrationReference.id.desc()
        )

        if offset is not None:
            query = query.offset(offset)
        if limit is not None:
            query = query.limit(limit)

        return list(self.db.scalars(query).all())

    def count(
        self,
        *,
        catalog: str | None = None,
        status: str | None = None,
        created_from: datetime | None = None,
        created_to: datetime | None = None,
        include_deleted: bool = False,
    ) -> int:
        query = self._build_query(
            catalog=catalog,
            status=status,
            created_from=created_from,
            created_to=created_to,
            include_deleted=include_deleted,
        )
        return self.db.scalar(select(func.count()).select_from(query.subquery())) or 0

    def update(
        self,
        reference_id: int,
        values: Mapping[str, object],
    ) -> AdministrationReference | None:
        reference = self.get_by_id(reference_id)
        if reference is None:
            return None

        unsupported_fields = set(values) - self._mutable_fields
        if unsupported_fields:
            fields = ", ".join(sorted(unsupported_fields))
            raise ValueError(
                f"Unsupported administration reference update fields: {fields}"
            )

        for field, value in values.items():
            setattr(reference, field, value)

        self.db.flush()
        return reference

    def delete(self, reference_id: int) -> bool:
        reference = self.get_by_id(reference_id)
        if reference is None:
            return False

        reference.deleted_at = datetime.now(timezone.utc)
        self.db.flush()
        return True

    def mark_deleted(self, reference_id: int) -> bool:
        return self.delete(reference_id)

    def exists(self, reference_id: int, *, include_deleted: bool = False) -> bool:
        return self.get_by_id(reference_id, include_deleted=include_deleted) is not None

    def health(self) -> bool:
        return self.db.scalar(select(1)) == 1

    def _build_query(
        self,
        *,
        catalog: str | None = None,
        status: str | None = None,
        created_from: datetime | None = None,
        created_to: datetime | None = None,
        include_deleted: bool = False,
    ) -> Select[tuple[AdministrationReference]]:
        query = select(AdministrationReference)

        if not include_deleted:
            query = query.where(AdministrationReference.deleted_at.is_(None))
        if catalog is not None:
            query = query.where(AdministrationReference.catalog == catalog)
        if status is not None:
            query = query.where(AdministrationReference.status == status)
        if created_from is not None:
            query = query.where(AdministrationReference.created_at >= created_from)
        if created_to is not None:
            query = query.where(AdministrationReference.created_at <= created_to)

        return query


class MaintenanceTaskRepository:
    """Persistence operations for administrative maintenance tasks."""

    _mutable_fields = frozenset(
        {
            "operation_type",
            "operation_name",
            "status",
            "requested_by_user_id",
            "payload",
            "result",
            "error_message",
            "started_at",
            "completed_at",
        },
    )

    def __init__(self, db: Session) -> None:
        self.db = db

    def create(self, task: MaintenanceTask) -> MaintenanceTask:
        self.db.add(task)
        self.db.flush()
        return task

    def create_task(self, task: MaintenanceTask) -> MaintenanceTask:
        return self.create(task)

    def get_by_id(
        self,
        task_id: int,
        *,
        include_deleted: bool = False,
    ) -> MaintenanceTask | None:
        task = self.db.get(MaintenanceTask, task_id)
        if task is not None and task.deleted_at is not None and not include_deleted:
            return None
        return task

    def get_by_uuid(
        self,
        task_uuid: UUID,
        *,
        include_deleted: bool = False,
    ) -> MaintenanceTask | None:
        query = select(MaintenanceTask).where(MaintenanceTask.task_uuid == task_uuid)
        if not include_deleted:
            query = query.where(MaintenanceTask.deleted_at.is_(None))
        return self.db.scalar(query)

    def list(
        self,
        *,
        operation_type: str | None = None,
        status: str | None = None,
        requested_by_user_id: int | None = None,
        requested_from: datetime | None = None,
        requested_to: datetime | None = None,
        created_from: datetime | None = None,
        created_to: datetime | None = None,
        include_deleted: bool = False,
        limit: int | None = None,
        offset: int | None = None,
    ) -> list[MaintenanceTask]:
        query = self._build_query(
            operation_type=operation_type,
            status=status,
            requested_by_user_id=requested_by_user_id,
            requested_from=requested_from,
            requested_to=requested_to,
            created_from=created_from,
            created_to=created_to,
            include_deleted=include_deleted,
        ).order_by(MaintenanceTask.created_at.desc(), MaintenanceTask.id.desc())

        if offset is not None:
            query = query.offset(offset)
        if limit is not None:
            query = query.limit(limit)

        return list(self.db.scalars(query).all())

    def count(
        self,
        *,
        operation_type: str | None = None,
        status: str | None = None,
        requested_by_user_id: int | None = None,
        requested_from: datetime | None = None,
        requested_to: datetime | None = None,
        created_from: datetime | None = None,
        created_to: datetime | None = None,
        include_deleted: bool = False,
    ) -> int:
        query = self._build_query(
            operation_type=operation_type,
            status=status,
            requested_by_user_id=requested_by_user_id,
            requested_from=requested_from,
            requested_to=requested_to,
            created_from=created_from,
            created_to=created_to,
            include_deleted=include_deleted,
        )
        return self.db.scalar(select(func.count()).select_from(query.subquery())) or 0

    def update(
        self, task_id: int, values: Mapping[str, object]
    ) -> MaintenanceTask | None:
        task = self.get_by_id(task_id)
        if task is None:
            return None

        unsupported_fields = set(values) - self._mutable_fields
        if unsupported_fields:
            fields = ", ".join(sorted(unsupported_fields))
            raise ValueError(f"Unsupported maintenance task update fields: {fields}")

        for field, value in values.items():
            setattr(task, field, value)

        self.db.flush()
        return task

    def delete(self, task_id: int) -> bool:
        task = self.get_by_id(task_id)
        if task is None:
            return False

        task.deleted_at = datetime.now(timezone.utc)
        self.db.flush()
        return True

    def mark_deleted(self, task_id: int) -> bool:
        return self.delete(task_id)

    def exists(self, task_id: int, *, include_deleted: bool = False) -> bool:
        return self.get_by_id(task_id, include_deleted=include_deleted) is not None

    def health(self) -> bool:
        return self.db.scalar(select(1)) == 1

    def _build_query(
        self,
        *,
        operation_type: str | None = None,
        status: str | None = None,
        requested_by_user_id: int | None = None,
        requested_from: datetime | None = None,
        requested_to: datetime | None = None,
        created_from: datetime | None = None,
        created_to: datetime | None = None,
        include_deleted: bool = False,
    ) -> Select[tuple[MaintenanceTask]]:
        query = select(MaintenanceTask)

        if not include_deleted:
            query = query.where(MaintenanceTask.deleted_at.is_(None))
        if operation_type is not None:
            query = query.where(MaintenanceTask.operation_type == operation_type)
        if status is not None:
            query = query.where(MaintenanceTask.status == status)
        if requested_by_user_id is not None:
            query = query.where(
                MaintenanceTask.requested_by_user_id == requested_by_user_id
            )
        if requested_from is not None:
            query = query.where(MaintenanceTask.requested_at >= requested_from)
        if requested_to is not None:
            query = query.where(MaintenanceTask.requested_at <= requested_to)
        if created_from is not None:
            query = query.where(MaintenanceTask.created_at >= created_from)
        if created_to is not None:
            query = query.where(MaintenanceTask.created_at <= created_to)

        return query


class AdminActionEventRepository:
    """Persistence operations for administrative action events."""

    def __init__(self, db: Session) -> None:
        self.db = db

    def create(self, event: AdminActionEvent) -> AdminActionEvent:
        self.db.add(event)
        self.db.flush()
        return event

    def create_event(self, event: AdminActionEvent) -> AdminActionEvent:
        return self.create(event)

    def get_by_id(self, event_id: int) -> AdminActionEvent | None:
        return self.db.get(AdminActionEvent, event_id)

    def get_by_uuid(self, event_uuid: UUID) -> AdminActionEvent | None:
        return self.db.scalar(
            select(AdminActionEvent).where(AdminActionEvent.event_uuid == event_uuid),
        )

    def list(
        self,
        *,
        action_type: str | None = None,
        status: str | None = None,
        target_type: str | None = None,
        target_id: str | None = None,
        actor_user_id: int | None = None,
        actor_username: str | None = None,
        correlation_id: str | None = None,
        request_id: str | None = None,
        created_from: datetime | None = None,
        created_to: datetime | None = None,
        limit: int | None = None,
        offset: int | None = None,
    ) -> list[AdminActionEvent]:
        query = self._build_query(
            action_type=action_type,
            status=status,
            target_type=target_type,
            target_id=target_id,
            actor_user_id=actor_user_id,
            actor_username=actor_username,
            correlation_id=correlation_id,
            request_id=request_id,
            created_from=created_from,
            created_to=created_to,
        ).order_by(AdminActionEvent.created_at.desc(), AdminActionEvent.id.desc())

        if offset is not None:
            query = query.offset(offset)
        if limit is not None:
            query = query.limit(limit)

        return list(self.db.scalars(query).all())

    def count(
        self,
        *,
        action_type: str | None = None,
        status: str | None = None,
        target_type: str | None = None,
        target_id: str | None = None,
        actor_user_id: int | None = None,
        actor_username: str | None = None,
        correlation_id: str | None = None,
        request_id: str | None = None,
        created_from: datetime | None = None,
        created_to: datetime | None = None,
    ) -> int:
        query = self._build_query(
            action_type=action_type,
            status=status,
            target_type=target_type,
            target_id=target_id,
            actor_user_id=actor_user_id,
            actor_username=actor_username,
            correlation_id=correlation_id,
            request_id=request_id,
            created_from=created_from,
            created_to=created_to,
        )
        return self.db.scalar(select(func.count()).select_from(query.subquery())) or 0

    def exists(self, event_id: int) -> bool:
        return self.get_by_id(event_id) is not None

    def health(self) -> bool:
        return self.db.scalar(select(1)) == 1

    def _build_query(
        self,
        *,
        action_type: str | None = None,
        status: str | None = None,
        target_type: str | None = None,
        target_id: str | None = None,
        actor_user_id: int | None = None,
        actor_username: str | None = None,
        correlation_id: str | None = None,
        request_id: str | None = None,
        created_from: datetime | None = None,
        created_to: datetime | None = None,
    ) -> Select[tuple[AdminActionEvent]]:
        query = select(AdminActionEvent)

        if action_type is not None:
            query = query.where(AdminActionEvent.action_type == action_type)
        if status is not None:
            query = query.where(AdminActionEvent.status == status)
        if target_type is not None:
            query = query.where(AdminActionEvent.target_type == target_type)
        if target_id is not None:
            query = query.where(AdminActionEvent.target_id == target_id)
        if actor_user_id is not None:
            query = query.where(AdminActionEvent.actor_user_id == actor_user_id)
        if actor_username is not None:
            query = query.where(AdminActionEvent.actor_username == actor_username)
        if correlation_id is not None:
            query = query.where(AdminActionEvent.correlation_id == correlation_id)
        if request_id is not None:
            query = query.where(AdminActionEvent.request_id == request_id)
        if created_from is not None:
            query = query.where(AdminActionEvent.created_at >= created_from)
        if created_to is not None:
            query = query.where(AdminActionEvent.created_at <= created_to)

        return query


class AdministrationRepository:
    """Persistence boundary for administration data and maintenance operations."""

    def __init__(self, db: Session) -> None:
        self.db = db
        self.references = AdministrationReferenceRepository(db)
        self.maintenance_tasks = MaintenanceTaskRepository(db)
        self.action_events = AdminActionEventRepository(db)

    def health(self) -> bool:
        """Return whether all administration persistence boundaries are available."""
        return (
            self.references.health()
            and self.maintenance_tasks.health()
            and self.action_events.health()
        )


__all__ = [
    "AdminActionEventRepository",
    "AdministrationReferenceRepository",
    "AdministrationRepository",
    "MaintenanceTaskRepository",
]
