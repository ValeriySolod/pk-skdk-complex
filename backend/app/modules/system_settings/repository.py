"""Repository operations for the System Settings module."""

from __future__ import annotations

from collections.abc import Mapping
from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import Select, func, select
from sqlalchemy.orm import Session

from app.modules.system_settings.models import (
    SystemSetting,
    SystemSettingChangeEvent,
    SystemSettingDefault,
)


class SystemSettingRepository:
    """Persistence operations for persisted system settings."""

    _mutable_fields = frozenset(
        {
            "category",
            "key",
            "title",
            "description",
            "value",
            "default_value",
            "value_type",
            "validation_rules",
            "metadata_json",
            "status",
            "updated_by_id",
            "deleted_by_id",
        },
    )

    def __init__(self, db: Session) -> None:
        self.db = db

    def create(self, setting: SystemSetting) -> SystemSetting:
        self.db.add(setting)
        self.db.flush()
        return setting

    def create_setting(self, setting: SystemSetting) -> SystemSetting:
        return self.create(setting)

    def get_by_id(
        self,
        setting_id: int,
        *,
        include_deleted: bool = False,
    ) -> SystemSetting | None:
        setting = self.db.get(SystemSetting, setting_id)
        if (
            setting is not None
            and setting.deleted_at is not None
            and not include_deleted
        ):
            return None
        return setting

    def get_by_uuid(
        self,
        setting_uuid: UUID,
        *,
        include_deleted: bool = False,
    ) -> SystemSetting | None:
        query = select(SystemSetting).where(SystemSetting.uuid == setting_uuid)
        if not include_deleted:
            query = query.where(SystemSetting.deleted_at.is_(None))
        return self.db.scalar(query)

    def get_by_key(
        self,
        category: str,
        key: str,
        *,
        include_deleted: bool = False,
    ) -> SystemSetting | None:
        query = select(SystemSetting).where(
            SystemSetting.category == category,
            SystemSetting.key == key,
        )
        if not include_deleted:
            query = query.where(SystemSetting.deleted_at.is_(None))
        return self.db.scalar(query)

    def list(
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
        query = self._build_query(
            category=category,
            key=key,
            status=status,
            value_type=value_type,
            created_by_id=created_by_id,
            updated_by_id=updated_by_id,
            created_from=created_from,
            created_to=created_to,
            include_deleted=include_deleted,
        ).order_by(SystemSetting.created_at.desc(), SystemSetting.id.desc())

        if offset is not None:
            query = query.offset(offset)
        if limit is not None:
            query = query.limit(limit)

        return list(self.db.scalars(query).all())

    def count(
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
        query = self._build_query(
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
        return self.db.scalar(select(func.count()).select_from(query.subquery())) or 0

    def update(
        self,
        setting_id: int,
        values: Mapping[str, object],
    ) -> SystemSetting | None:
        setting = self.get_by_id(setting_id)
        if setting is None:
            return None

        unsupported_fields = set(values) - self._mutable_fields
        if unsupported_fields:
            fields = ", ".join(sorted(unsupported_fields))
            raise ValueError(f"Unsupported system setting update fields: {fields}")

        for field, value in values.items():
            setattr(setting, field, value)

        self.db.flush()
        return setting

    def delete(self, setting_id: int, *, deleted_by_id: int | None = None) -> bool:
        setting = self.get_by_id(setting_id)
        if setting is None:
            return False

        setting.deleted_at = datetime.now(timezone.utc)
        if deleted_by_id is not None:
            setting.deleted_by_id = deleted_by_id
        self.db.flush()
        return True

    def mark_deleted(
        self,
        setting_id: int,
        *,
        deleted_by_id: int | None = None,
    ) -> bool:
        return self.delete(setting_id, deleted_by_id=deleted_by_id)

    def exists(self, setting_id: int, *, include_deleted: bool = False) -> bool:
        return self.get_by_id(setting_id, include_deleted=include_deleted) is not None

    def health(self) -> bool:
        return self.db.scalar(select(1)) == 1

    def _build_query(
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
    ) -> Select[tuple[SystemSetting]]:
        query = select(SystemSetting)

        if not include_deleted:
            query = query.where(SystemSetting.deleted_at.is_(None))
        if category is not None:
            query = query.where(SystemSetting.category == category)
        if key is not None:
            query = query.where(SystemSetting.key == key)
        if status is not None:
            query = query.where(SystemSetting.status == status)
        if value_type is not None:
            query = query.where(SystemSetting.value_type == value_type)
        if created_by_id is not None:
            query = query.where(SystemSetting.created_by_id == created_by_id)
        if updated_by_id is not None:
            query = query.where(SystemSetting.updated_by_id == updated_by_id)
        if created_from is not None:
            query = query.where(SystemSetting.created_at >= created_from)
        if created_to is not None:
            query = query.where(SystemSetting.created_at <= created_to)

        return query


class SystemSettingDefaultRepository:
    """Persistence operations for system setting default definitions."""

    _mutable_fields = frozenset(
        {
            "category",
            "key",
            "title",
            "description",
            "default_value",
            "value_type",
            "validation_rules",
            "status",
            "metadata_json",
        },
    )

    def __init__(self, db: Session) -> None:
        self.db = db

    def create(self, default: SystemSettingDefault) -> SystemSettingDefault:
        self.db.add(default)
        self.db.flush()
        return default

    def create_default(self, default: SystemSettingDefault) -> SystemSettingDefault:
        return self.create(default)

    def get_by_id(self, default_id: int) -> SystemSettingDefault | None:
        return self.db.get(SystemSettingDefault, default_id)

    def get_by_uuid(self, default_uuid: UUID) -> SystemSettingDefault | None:
        return self.db.scalar(
            select(SystemSettingDefault).where(
                SystemSettingDefault.uuid == default_uuid,
            ),
        )

    def get_by_key(self, category: str, key: str) -> SystemSettingDefault | None:
        return self.db.scalar(
            select(SystemSettingDefault).where(
                SystemSettingDefault.category == category,
                SystemSettingDefault.key == key,
            ),
        )

    def list(
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
        query = self._build_query(
            category=category,
            key=key,
            status=status,
            value_type=value_type,
            created_from=created_from,
            created_to=created_to,
        ).order_by(
            SystemSettingDefault.created_at.desc(),
            SystemSettingDefault.id.desc(),
        )

        if offset is not None:
            query = query.offset(offset)
        if limit is not None:
            query = query.limit(limit)

        return list(self.db.scalars(query).all())

    def count(
        self,
        *,
        category: str | None = None,
        key: str | None = None,
        status: str | None = None,
        value_type: str | None = None,
        created_from: datetime | None = None,
        created_to: datetime | None = None,
    ) -> int:
        query = self._build_query(
            category=category,
            key=key,
            status=status,
            value_type=value_type,
            created_from=created_from,
            created_to=created_to,
        )
        return self.db.scalar(select(func.count()).select_from(query.subquery())) or 0

    def update(
        self,
        default_id: int,
        values: Mapping[str, object],
    ) -> SystemSettingDefault | None:
        default = self.get_by_id(default_id)
        if default is None:
            return None

        unsupported_fields = set(values) - self._mutable_fields
        if unsupported_fields:
            fields = ", ".join(sorted(unsupported_fields))
            raise ValueError(
                f"Unsupported system setting default update fields: {fields}"
            )

        for field, value in values.items():
            setattr(default, field, value)

        self.db.flush()
        return default

    def exists(self, default_id: int) -> bool:
        return self.get_by_id(default_id) is not None

    def health(self) -> bool:
        return self.db.scalar(select(1)) == 1

    def _build_query(
        self,
        *,
        category: str | None = None,
        key: str | None = None,
        status: str | None = None,
        value_type: str | None = None,
        created_from: datetime | None = None,
        created_to: datetime | None = None,
    ) -> Select[tuple[SystemSettingDefault]]:
        query = select(SystemSettingDefault)

        if category is not None:
            query = query.where(SystemSettingDefault.category == category)
        if key is not None:
            query = query.where(SystemSettingDefault.key == key)
        if status is not None:
            query = query.where(SystemSettingDefault.status == status)
        if value_type is not None:
            query = query.where(SystemSettingDefault.value_type == value_type)
        if created_from is not None:
            query = query.where(SystemSettingDefault.created_at >= created_from)
        if created_to is not None:
            query = query.where(SystemSettingDefault.created_at <= created_to)

        return query


class SystemSettingChangeEventRepository:
    """Persistence operations for append-only system setting change events."""

    def __init__(self, db: Session) -> None:
        self.db = db

    def create(self, event: SystemSettingChangeEvent) -> SystemSettingChangeEvent:
        self.db.add(event)
        self.db.flush()
        return event

    def create_event(self, event: SystemSettingChangeEvent) -> SystemSettingChangeEvent:
        return self.create(event)

    def get_by_id(self, event_id: int) -> SystemSettingChangeEvent | None:
        return self.db.get(SystemSettingChangeEvent, event_id)

    def get_by_uuid(self, event_uuid: UUID) -> SystemSettingChangeEvent | None:
        return self.db.scalar(
            select(SystemSettingChangeEvent).where(
                SystemSettingChangeEvent.event_uuid == event_uuid,
            ),
        )

    def list(
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
        query = self._build_query(
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
        ).order_by(
            SystemSettingChangeEvent.created_at.desc(),
            SystemSettingChangeEvent.id.desc(),
        )

        if offset is not None:
            query = query.offset(offset)
        if limit is not None:
            query = query.limit(limit)

        return list(self.db.scalars(query).all())

    def count(
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
        query = self._build_query(
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
        return self.db.scalar(select(func.count()).select_from(query.subquery())) or 0

    def exists(self, event_id: int) -> bool:
        return self.get_by_id(event_id) is not None

    def health(self) -> bool:
        return self.db.scalar(select(1)) == 1

    def _build_query(
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
    ) -> Select[tuple[SystemSettingChangeEvent]]:
        query = select(SystemSettingChangeEvent)

        if system_setting_id is not None:
            query = query.where(
                SystemSettingChangeEvent.system_setting_id == system_setting_id
            )
        if category is not None:
            query = query.where(SystemSettingChangeEvent.category == category)
        if key is not None:
            query = query.where(SystemSettingChangeEvent.key == key)
        if action is not None:
            query = query.where(SystemSettingChangeEvent.action == action)
        if actor_user_id is not None:
            query = query.where(SystemSettingChangeEvent.actor_user_id == actor_user_id)
        if source is not None:
            query = query.where(SystemSettingChangeEvent.source == source)
        if request_id is not None:
            query = query.where(SystemSettingChangeEvent.request_id == request_id)
        if correlation_id is not None:
            query = query.where(
                SystemSettingChangeEvent.correlation_id == correlation_id
            )
        if created_from is not None:
            query = query.where(SystemSettingChangeEvent.created_at >= created_from)
        if created_to is not None:
            query = query.where(SystemSettingChangeEvent.created_at <= created_to)

        return query


class SystemSettingsRepository:
    """Persistence boundary for system settings."""

    def __init__(self, db: Session) -> None:
        self.db = db
        self.settings = SystemSettingRepository(db)
        self.defaults = SystemSettingDefaultRepository(db)
        self.change_events = SystemSettingChangeEventRepository(db)

    def health(self) -> bool:
        """Return whether all system settings persistence boundaries are available."""
        return (
            self.settings.health()
            and self.defaults.health()
            and self.change_events.health()
        )

    def health_check(self) -> bool:
        return self.health()


__all__ = [
    "SystemSettingChangeEventRepository",
    "SystemSettingDefaultRepository",
    "SystemSettingRepository",
    "SystemSettingsRepository",
]
