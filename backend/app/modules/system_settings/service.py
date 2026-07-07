"""Service layer for the System Settings module."""

from __future__ import annotations

from collections.abc import Mapping
from datetime import datetime
from typing import Any
from uuid import UUID

from app.modules.system_settings.models import (
    SystemSetting,
    SystemSettingChangeEvent,
    SystemSettingDefault,
)
from app.modules.system_settings.repository import SystemSettingsRepository

Payload = Mapping[str, Any]


class SystemSettingsService:
    """Business boundary for configurable application settings and defaults."""

    def __init__(self, repository: SystemSettingsRepository) -> None:
        self.repository = repository
        self.settings = repository.settings
        self.defaults = repository.defaults
        self.change_events = repository.change_events

    def health(self) -> dict[str, Any]:
        """Return aggregate System Settings module health."""

        repository_checks = {
            "settings": self.settings.health(),
            "defaults": self.defaults.health(),
            "change_events": self.change_events.health(),
        }
        return {
            "module": "system_settings",
            "status": "ok" if all(repository_checks.values()) else "error",
            "repositories": repository_checks,
        }

    # Settings

    def create_setting(self, payload: Payload | SystemSetting) -> SystemSetting:
        """Create a persisted system setting."""

        setting = (
            payload
            if isinstance(payload, SystemSetting)
            else SystemSetting(**dict(payload))
        )
        return self.settings.create_setting(setting)

    def get_setting(
        self,
        setting_id: int,
        *,
        include_deleted: bool = False,
    ) -> SystemSetting | None:
        """Get a system setting by integer ID."""

        return self.settings.get_by_id(setting_id, include_deleted=include_deleted)

    def get_setting_by_id(
        self,
        setting_id: int,
        *,
        include_deleted: bool = False,
    ) -> SystemSetting | None:
        """Get a system setting by integer ID."""

        return self.get_setting(setting_id, include_deleted=include_deleted)

    def get_setting_by_uuid(
        self,
        setting_uuid: UUID,
        *,
        include_deleted: bool = False,
    ) -> SystemSetting | None:
        """Get a system setting by UUID."""

        return self.settings.get_by_uuid(setting_uuid, include_deleted=include_deleted)

    def get_setting_by_key(
        self,
        category: str,
        key: str,
        *,
        include_deleted: bool = False,
    ) -> SystemSetting | None:
        """Get a system setting by category and key."""

        return self.settings.get_by_key(category, key, include_deleted=include_deleted)

    def list_settings(
        self,
        *,
        category: str | None = None,
        key: str | None = None,
        status: str | None = None,
        value_type: str | None = None,
        created_by_id: int | None = None,
        updated_by_id: int | None = None,
        created_from: datetime | None = None,
        created_to: datetime | None = None,
        include_deleted: bool = False,
        limit: int | None = None,
        offset: int | None = None,
    ) -> list[SystemSetting]:
        """List system settings using repository filters."""

        return self.settings.list(
            category=category,
            key=key,
            status=status,
            value_type=value_type,
            created_by_id=created_by_id,
            updated_by_id=updated_by_id,
            created_from=created_from,
            created_to=created_to,
            include_deleted=include_deleted,
            limit=limit,
            offset=offset,
        )

    def count_settings(
        self,
        *,
        category: str | None = None,
        key: str | None = None,
        status: str | None = None,
        value_type: str | None = None,
        created_by_id: int | None = None,
        updated_by_id: int | None = None,
        created_from: datetime | None = None,
        created_to: datetime | None = None,
        include_deleted: bool = False,
    ) -> int:
        """Count system settings using repository filters."""

        return self.settings.count(
            category=category,
            key=key,
            status=status,
            value_type=value_type,
            created_by_id=created_by_id,
            updated_by_id=updated_by_id,
            created_from=created_from,
            created_to=created_to,
            include_deleted=include_deleted,
        )

    def update_setting(
        self,
        setting_id: int,
        values: Payload,
    ) -> SystemSetting | None:
        """Update mutable system setting fields."""

        return self.settings.update(setting_id, values)

    def delete_setting(
        self,
        setting_id: int,
        *,
        deleted_by_id: int | None = None,
    ) -> bool:
        """Soft-delete a system setting."""

        return self.settings.delete(setting_id, deleted_by_id=deleted_by_id)

    def mark_setting_deleted(
        self,
        setting_id: int,
        *,
        deleted_by_id: int | None = None,
    ) -> bool:
        """Soft-delete a system setting using lifecycle alias."""

        return self.settings.mark_deleted(setting_id, deleted_by_id=deleted_by_id)

    def setting_exists(
        self,
        setting_id: int,
        *,
        include_deleted: bool = False,
    ) -> bool:
        """Return whether a system setting exists."""

        return self.settings.exists(setting_id, include_deleted=include_deleted)

    # Defaults

    def create_default(
        self, payload: Payload | SystemSettingDefault
    ) -> SystemSettingDefault:
        """Create a system setting default definition."""

        default = (
            payload
            if isinstance(payload, SystemSettingDefault)
            else SystemSettingDefault(**dict(payload))
        )
        return self.defaults.create_default(default)

    def get_default(self, default_id: int) -> SystemSettingDefault | None:
        """Get a default definition by integer ID."""

        return self.defaults.get_by_id(default_id)

    def get_default_by_id(self, default_id: int) -> SystemSettingDefault | None:
        """Get a default definition by integer ID."""

        return self.get_default(default_id)

    def get_default_by_uuid(self, default_uuid: UUID) -> SystemSettingDefault | None:
        """Get a default definition by UUID."""

        return self.defaults.get_by_uuid(default_uuid)

    def get_default_by_key(
        self, category: str, key: str
    ) -> SystemSettingDefault | None:
        """Get a default definition by category and key."""

        return self.defaults.get_by_key(category, key)

    def list_defaults(
        self,
        *,
        category: str | None = None,
        key: str | None = None,
        status: str | None = None,
        value_type: str | None = None,
        created_from: datetime | None = None,
        created_to: datetime | None = None,
        limit: int | None = None,
        offset: int | None = None,
    ) -> list[SystemSettingDefault]:
        """List default definitions using repository filters."""

        return self.defaults.list(
            category=category,
            key=key,
            status=status,
            value_type=value_type,
            created_from=created_from,
            created_to=created_to,
            limit=limit,
            offset=offset,
        )

    def count_defaults(
        self,
        *,
        category: str | None = None,
        key: str | None = None,
        status: str | None = None,
        value_type: str | None = None,
        created_from: datetime | None = None,
        created_to: datetime | None = None,
    ) -> int:
        """Count default definitions using repository filters."""

        return self.defaults.count(
            category=category,
            key=key,
            status=status,
            value_type=value_type,
            created_from=created_from,
            created_to=created_to,
        )

    def update_default(
        self,
        default_id: int,
        values: Payload,
    ) -> SystemSettingDefault | None:
        """Update mutable default definition fields."""

        return self.defaults.update(default_id, values)

    def default_exists(self, default_id: int) -> bool:
        """Return whether a default definition exists."""

        return self.defaults.exists(default_id)

    # Change events

    def create_change_event(
        self,
        payload: Payload | SystemSettingChangeEvent,
    ) -> SystemSettingChangeEvent:
        """Create an append-only setting change event."""

        event = (
            payload
            if isinstance(payload, SystemSettingChangeEvent)
            else SystemSettingChangeEvent(**dict(payload))
        )
        return self.change_events.create_event(event)

    def get_change_event(self, event_id: int) -> SystemSettingChangeEvent | None:
        """Get a setting change event by integer ID."""

        return self.change_events.get_by_id(event_id)

    def get_change_event_by_id(self, event_id: int) -> SystemSettingChangeEvent | None:
        """Get a setting change event by integer ID."""

        return self.get_change_event(event_id)

    def get_change_event_by_uuid(
        self,
        event_uuid: UUID,
    ) -> SystemSettingChangeEvent | None:
        """Get a setting change event by UUID."""

        return self.change_events.get_by_uuid(event_uuid)

    def list_change_events(
        self,
        *,
        system_setting_id: int | None = None,
        category: str | None = None,
        key: str | None = None,
        action: str | None = None,
        actor_user_id: int | None = None,
        source: str | None = None,
        request_id: str | None = None,
        correlation_id: str | None = None,
        created_from: datetime | None = None,
        created_to: datetime | None = None,
        limit: int | None = None,
        offset: int | None = None,
    ) -> list[SystemSettingChangeEvent]:
        """List setting change events using repository filters."""

        return self.change_events.list(
            system_setting_id=system_setting_id,
            category=category,
            key=key,
            action=action,
            actor_user_id=actor_user_id,
            source=source,
            request_id=request_id,
            correlation_id=correlation_id,
            created_from=created_from,
            created_to=created_to,
            limit=limit,
            offset=offset,
        )

    def count_change_events(
        self,
        *,
        system_setting_id: int | None = None,
        category: str | None = None,
        key: str | None = None,
        action: str | None = None,
        actor_user_id: int | None = None,
        source: str | None = None,
        request_id: str | None = None,
        correlation_id: str | None = None,
        created_from: datetime | None = None,
        created_to: datetime | None = None,
    ) -> int:
        """Count setting change events using repository filters."""

        return self.change_events.count(
            system_setting_id=system_setting_id,
            category=category,
            key=key,
            action=action,
            actor_user_id=actor_user_id,
            source=source,
            request_id=request_id,
            correlation_id=correlation_id,
            created_from=created_from,
            created_to=created_to,
        )

    def change_event_exists(self, event_id: int) -> bool:
        """Return whether a setting change event exists."""

        return self.change_events.exists(event_id)

    # Compatibility aliases
    create_system_setting = create_setting
    get_system_setting = get_setting
    get_system_setting_by_id = get_setting_by_id
    get_system_setting_by_uuid = get_setting_by_uuid
    get_system_setting_by_key = get_setting_by_key
    list_system_settings = list_settings
    count_system_settings = count_settings
    update_system_setting = update_setting
    delete_system_setting = delete_setting
    mark_system_setting_deleted = mark_setting_deleted
    system_setting_exists = setting_exists

    create_setting_default = create_default
    get_setting_default = get_default
    get_setting_default_by_id = get_default_by_id
    get_setting_default_by_uuid = get_default_by_uuid
    get_setting_default_by_key = get_default_by_key
    list_setting_defaults = list_defaults
    count_setting_defaults = count_defaults
    update_setting_default = update_default
    setting_default_exists = default_exists

    create_event = create_change_event
    get_event = get_change_event
    get_event_by_id = get_change_event_by_id
    get_event_by_uuid = get_change_event_by_uuid
    list_events = list_change_events
    count_events = count_change_events
    event_exists = change_event_exists
