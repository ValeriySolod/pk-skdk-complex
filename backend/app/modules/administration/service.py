"""Application service layer for the Administration module."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any
from uuid import UUID

from sqlalchemy.orm import Session

from app.modules.administration.models import (
    AdminActionEvent,
    AdministrationReference,
    MaintenanceTask,
)
from app.modules.administration.repository import (
    AdminActionEventRepository,
    AdministrationReferenceRepository,
    MaintenanceTaskRepository,
)


Payload = Mapping[str, Any]


class AdministrationService:
    """Service boundary for administration references, maintenance tasks, and action events."""

    def __init__(self, db: Session) -> None:
        self.db = db
        self.references = AdministrationReferenceRepository(db)
        self.maintenance_tasks = MaintenanceTaskRepository(db)
        self.action_events = AdminActionEventRepository(db)

    # ------------------------------------------------------------------
    # Health
    # ------------------------------------------------------------------

    def health(self) -> dict[str, Any]:
        """Return aggregate Administration module health."""

        repository_checks = {
            "references": self.references.health(),
            "maintenance_tasks": self.maintenance_tasks.health(),
            "action_events": self.action_events.health(),
        }

        return {
            "module": "administration",
            "status": "ok" if all(repository_checks.values()) else "error",
            "repositories": repository_checks,
        }

    # ------------------------------------------------------------------
    # Administration references
    # ------------------------------------------------------------------

    def create_reference(self, payload: Payload) -> AdministrationReference:
        """Create an administration reference."""

        reference = AdministrationReference(**dict(payload))
        return self.references.create(reference)

    def get_reference(
        self,
        reference_id: int,
        *,
        include_deleted: bool = False,
    ) -> AdministrationReference | None:
        """Get an administration reference by integer ID."""

        return self.references.get_by_id(
            reference_id,
            include_deleted=include_deleted,
        )

    def get_reference_by_uuid(
        self,
        reference_uuid: UUID,
        *,
        include_deleted: bool = False,
    ) -> AdministrationReference | None:
        """Get an administration reference by UUID."""

        return self.references.get_by_uuid(
            reference_uuid,
            include_deleted=include_deleted,
        )

    def get_reference_by_code(
        self,
        code: str,
        *,
        include_deleted: bool = False,
    ) -> AdministrationReference | None:
        """Get an administration reference by business code."""

        return self.references.get_by_code(
            code,
            include_deleted=include_deleted,
        )

    def list_references(
        self,
        *,
        catalog: str | None = None,
        status: str | None = None,
        created_from: Any | None = None,
        created_to: Any | None = None,
        include_deleted: bool = False,
        limit: int | None = None,
        offset: int | None = None,
    ) -> list[AdministrationReference]:
        """List administration references."""

        return self.references.list(
            catalog=catalog,
            status=status,
            created_from=created_from,
            created_to=created_to,
            include_deleted=include_deleted,
            limit=limit,
            offset=offset,
        )

    def count_references(
        self,
        *,
        catalog: str | None = None,
        status: str | None = None,
        created_from: Any | None = None,
        created_to: Any | None = None,
        include_deleted: bool = False,
    ) -> int:
        """Count administration references."""

        return self.references.count(
            catalog=catalog,
            status=status,
            created_from=created_from,
            created_to=created_to,
            include_deleted=include_deleted,
        )

    def update_reference(
        self,
        reference_id: int,
        payload: Payload,
    ) -> AdministrationReference | None:
        """Update an administration reference."""

        values = self._clean_payload(payload)
        if not values:
            return self.get_reference(reference_id)

        return self.references.update(reference_id, values)

    def delete_reference(self, reference_id: int) -> bool:
        """Soft-delete an administration reference."""

        return self.references.delete(reference_id)

    def mark_reference_deleted(self, reference_id: int) -> bool:
        """Soft-delete an administration reference."""

        return self.references.mark_deleted(reference_id)

    def reference_exists(
        self,
        reference_id: int,
        *,
        include_deleted: bool = False,
    ) -> bool:
        """Return whether an administration reference exists."""

        return self.references.exists(
            reference_id,
            include_deleted=include_deleted,
        )

    # Compatibility aliases
    create_administration_reference = create_reference
    get_administration_reference = get_reference
    list_administration_references = list_references
    count_administration_references = count_references
    update_administration_reference = update_reference
    delete_administration_reference = delete_reference
    administration_reference_exists = reference_exists

    # ------------------------------------------------------------------
    # Maintenance tasks
    # ------------------------------------------------------------------

    def create_maintenance_task(self, payload: Payload) -> MaintenanceTask:
        """Create a maintenance task."""

        task = MaintenanceTask(**dict(payload))
        return self.maintenance_tasks.create(task)

    def get_maintenance_task(
        self,
        task_id: int,
        *,
        include_deleted: bool = False,
    ) -> MaintenanceTask | None:
        """Get a maintenance task by integer ID."""

        return self.maintenance_tasks.get_by_id(
            task_id,
            include_deleted=include_deleted,
        )

    def get_maintenance_task_by_uuid(
        self,
        task_uuid: UUID,
        *,
        include_deleted: bool = False,
    ) -> MaintenanceTask | None:
        """Get a maintenance task by UUID."""

        return self.maintenance_tasks.get_by_uuid(
            task_uuid,
            include_deleted=include_deleted,
        )

    def list_maintenance_tasks(
        self,
        *,
        operation_type: str | None = None,
        status: str | None = None,
        requested_by_user_id: int | None = None,
        requested_from: Any | None = None,
        requested_to: Any | None = None,
        created_from: Any | None = None,
        created_to: Any | None = None,
        include_deleted: bool = False,
        limit: int | None = None,
        offset: int | None = None,
    ) -> list[MaintenanceTask]:
        """List maintenance tasks."""

        return self.maintenance_tasks.list(
            operation_type=operation_type,
            status=status,
            requested_by_user_id=requested_by_user_id,
            requested_from=requested_from,
            requested_to=requested_to,
            created_from=created_from,
            created_to=created_to,
            include_deleted=include_deleted,
            limit=limit,
            offset=offset,
        )

    def count_maintenance_tasks(
        self,
        *,
        operation_type: str | None = None,
        status: str | None = None,
        requested_by_user_id: int | None = None,
        requested_from: Any | None = None,
        requested_to: Any | None = None,
        created_from: Any | None = None,
        created_to: Any | None = None,
        include_deleted: bool = False,
    ) -> int:
        """Count maintenance tasks."""

        return self.maintenance_tasks.count(
            operation_type=operation_type,
            status=status,
            requested_by_user_id=requested_by_user_id,
            requested_from=requested_from,
            requested_to=requested_to,
            created_from=created_from,
            created_to=created_to,
            include_deleted=include_deleted,
        )

    def update_maintenance_task(
        self,
        task_id: int,
        payload: Payload,
    ) -> MaintenanceTask | None:
        """Update a maintenance task."""

        values = self._clean_payload(payload)
        if not values:
            return self.get_maintenance_task(task_id)

        return self.maintenance_tasks.update(task_id, values)

    def delete_maintenance_task(self, task_id: int) -> bool:
        """Soft-delete a maintenance task."""

        return self.maintenance_tasks.delete(task_id)

    def mark_maintenance_task_deleted(self, task_id: int) -> bool:
        """Soft-delete a maintenance task."""

        return self.maintenance_tasks.mark_deleted(task_id)

    def maintenance_task_exists(
        self,
        task_id: int,
        *,
        include_deleted: bool = False,
    ) -> bool:
        """Return whether a maintenance task exists."""

        return self.maintenance_tasks.exists(
            task_id,
            include_deleted=include_deleted,
        )

    # Compatibility aliases
    create_task = create_maintenance_task
    get_task = get_maintenance_task
    list_tasks = list_maintenance_tasks
    count_tasks = count_maintenance_tasks
    update_task = update_maintenance_task
    delete_task = delete_maintenance_task
    task_exists = maintenance_task_exists

    # ------------------------------------------------------------------
    # Admin action events
    # ------------------------------------------------------------------

    def create_action_event(self, payload: Payload) -> AdminActionEvent:
        """Create an append-oriented administration action event."""

        event = AdminActionEvent(**dict(payload))
        return self.action_events.create(event)

    def get_action_event(self, event_id: int) -> AdminActionEvent | None:
        """Get an action event by integer ID."""

        return self.action_events.get_by_id(event_id)

    def get_action_event_by_uuid(self, event_uuid: UUID) -> AdminActionEvent | None:
        """Get an action event by UUID."""

        return self.action_events.get_by_uuid(event_uuid)

    def list_action_events(
        self,
        *,
        actor_user_id: int | None = None,
        action: str | None = None,
        entity_type: str | None = None,
        entity_id: str | None = None,
        created_from: Any | None = None,
        created_to: Any | None = None,
        limit: int | None = None,
        offset: int | None = None,
    ) -> list[AdminActionEvent]:
        """List administration action events."""

        return self.action_events.list(
            actor_user_id=actor_user_id,
            action=action,
            entity_type=entity_type,
            entity_id=entity_id,
            created_from=created_from,
            created_to=created_to,
            limit=limit,
            offset=offset,
        )

    def count_action_events(
        self,
        *,
        actor_user_id: int | None = None,
        action: str | None = None,
        entity_type: str | None = None,
        entity_id: str | None = None,
        created_from: Any | None = None,
        created_to: Any | None = None,
    ) -> int:
        """Count administration action events."""

        return self.action_events.count(
            actor_user_id=actor_user_id,
            action=action,
            entity_type=entity_type,
            entity_id=entity_id,
            created_from=created_from,
            created_to=created_to,
        )

    def action_event_exists(self, event_id: int) -> bool:
        """Return whether an action event exists."""

        return self.action_events.exists(event_id)

    # Compatibility aliases
    append_action_event = create_action_event
    record_action_event = create_action_event
    create_admin_action_event = create_action_event
    get_admin_action_event = get_action_event
    list_admin_action_events = list_action_events
    count_admin_action_events = count_action_events
    admin_action_event_exists = action_event_exists

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _clean_payload(payload: Payload) -> dict[str, Any]:
        """Remove None values from update payloads."""

        return {key: value for key, value in dict(payload).items() if value is not None}
