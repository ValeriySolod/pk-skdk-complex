from __future__ import annotations

from datetime import datetime
from uuid import uuid4

import pytest
from sqlalchemy.orm import Session

from app.models import User
from app.modules.system_settings.models import (
    SystemSetting,
    SystemSettingChangeAction,
    SystemSettingChangeEvent,
    SystemSettingDefaultStatus,
    SystemSettingStatus,
    SystemSettingValueType,
)
from app.modules.system_settings.repository import SystemSettingsRepository
from app.modules.system_settings.service import SystemSettingsService


@pytest.fixture()
def service(db_session: Session) -> SystemSettingsService:
    return SystemSettingsService(SystemSettingsRepository(db_session))


def create_test_user(
    db_session: Session,
    username: str = "system-settings-service-user",
) -> User:
    user = User(
        username=username,
        full_name="System Settings Service User",
        password_hash="not-used",
        role="test",
        is_active=True,
    )
    db_session.add(user)
    db_session.flush()
    return user


def create_setting(
    service: SystemSettingsService,
    *,
    category: str = "security",
    key: str = "password_policy",
    status: str = SystemSettingStatus.ACTIVE.value,
    value_type: str = SystemSettingValueType.OBJECT.value,
    created_by_id: int | None = None,
    updated_by_id: int | None = None,
    created_at: datetime | None = None,
) -> SystemSetting:
    return service.create_setting(
        {
            "category": category,
            "key": key,
            "title": "Password policy",
            "description": "Rules for account passwords",
            "value": {"minLength": 12, "classes": ["upper", "digit"]},
            "default_value": {"minLength": 10},
            "value_type": value_type,
            "validation_rules": {"required": ["minLength"]},
            "metadata_json": {"scope": "global", "labels": ["auth"]},
            "status": status,
            "created_by_id": created_by_id,
            "updated_by_id": updated_by_id,
            "created_at": created_at,
        }
    )


def test_system_settings_service_setting_lifecycle_filters_and_json_preservation(
    service: SystemSettingsService,
    db_session: Session,
) -> None:
    creator = create_test_user(db_session)
    updater = create_test_user(db_session, "system-settings-service-updater")
    first = create_setting(
        service,
        created_by_id=creator.id,
        updated_by_id=updater.id,
        created_at=datetime(2026, 7, 5, 9, 0, 0),
    )
    second = create_setting(
        service,
        category="notifications",
        key="email_enabled",
        value_type=SystemSettingValueType.BOOLEAN.value,
        created_by_id=creator.id,
        updated_by_id=creator.id,
        created_at=datetime(2026, 7, 5, 10, 0, 0),
    )
    original_uuid = first.uuid

    assert service.health() == {
        "module": "system_settings",
        "status": "ok",
        "repositories": {
            "settings": True,
            "defaults": True,
            "change_events": True,
        },
    }
    assert service.get_setting(first.id) == first
    assert service.get_setting_by_id(first.id) == first
    assert service.get_setting_by_uuid(original_uuid) == first
    assert service.get_setting_by_key("security", "password_policy") == first
    assert service.get_setting(999) is None
    assert service.get_setting_by_uuid(uuid4()) is None
    assert service.setting_exists(first.id) is True
    assert service.setting_exists(999) is False
    assert service.list_settings() == [second, first]
    assert service.list_system_settings(limit=1) == [second]
    assert service.list_settings(offset=1, limit=1) == [first]
    assert service.list_settings(category="security") == [first]
    assert service.list_settings(key="email_enabled") == [second]
    assert service.list_settings(created_by_id=creator.id) == [second, first]
    assert service.list_settings(updated_by_id=updater.id) == [first]
    assert service.list_settings(created_from=datetime(2026, 7, 5, 10, 0, 0)) == [
        second
    ]
    assert service.list_settings(created_to=datetime(2026, 7, 5, 9, 0, 0)) == [first]
    assert service.count_settings(status=SystemSettingStatus.ACTIVE.value) == 2
    assert service.count_settings(value_type=SystemSettingValueType.BOOLEAN.value) == 1
    assert service.count_settings(category="security", created_by_id=creator.id) == 1
    assert service.count_system_settings(key="missing") == 0

    updated = service.update_setting(
        first.id,
        {
            "value": {"minLength": 14, "classes": ["upper", "digit", "symbol"]},
            "metadata_json": {"scope": "tenant", "flags": {"sensitive": True}},
        },
    )

    assert updated is first
    assert first.uuid == original_uuid
    assert first.value == {"minLength": 14, "classes": ["upper", "digit", "symbol"]}
    assert first.metadata_json == {"scope": "tenant", "flags": {"sensitive": True}}
    assert service.update_setting(999, {"title": "Missing"}) is None
    with pytest.raises(
        ValueError, match="Unsupported system setting update fields: id"
    ):
        service.update_setting(first.id, {"id": 999})

    assert service.mark_setting_deleted(first.id, deleted_by_id=42) is True
    assert first.deleted_at is not None
    assert first.deleted_by_id == 42
    assert service.get_setting(first.id) is None
    assert service.get_setting(first.id, include_deleted=True) == first
    assert service.count_settings() == 1
    assert service.count_settings(include_deleted=True) == 2
    assert service.setting_exists(first.id) is False
    assert service.setting_exists(first.id, include_deleted=True) is True
    assert service.delete_setting(999) is False


def test_system_settings_service_defaults_lookup_filters_and_update(
    service: SystemSettingsService,
) -> None:
    first = service.create_default(
        {
            "category": "security",
            "key": "password_policy",
            "title": "Default password policy",
            "default_value": {"minLength": 12},
            "value_type": SystemSettingValueType.OBJECT.value,
            "validation_rules": {"minimum": 8},
            "metadata_json": {"source": "baseline"},
            "status": SystemSettingDefaultStatus.ACTIVE.value,
            "created_at": datetime(2026, 7, 5, 9, 0, 0),
        }
    )
    second = service.create_default(
        {
            "category": "notifications",
            "key": "email_enabled",
            "title": "Email enabled",
            "default_value": True,
            "value_type": SystemSettingValueType.BOOLEAN.value,
            "status": SystemSettingDefaultStatus.INACTIVE.value,
            "created_at": datetime(2026, 7, 5, 10, 0, 0),
        }
    )

    assert service.get_default(first.id) == first
    assert service.get_default_by_id(first.id) == first
    assert service.get_default_by_uuid(first.uuid) == first
    assert service.get_default_by_key("security", "password_policy") == first
    assert service.get_default(999) is None
    assert service.get_default_by_uuid(uuid4()) is None
    assert service.default_exists(first.id) is True
    assert service.default_exists(999) is False
    assert service.list_defaults() == [second, first]
    assert service.list_setting_defaults(limit=1) == [second]
    assert service.list_defaults(offset=1, limit=1) == [first]
    assert service.list_defaults(category="notifications") == [second]
    assert service.list_defaults(key="password_policy") == [first]
    assert service.list_defaults(status=SystemSettingDefaultStatus.ACTIVE.value) == [
        first
    ]
    assert service.list_defaults(created_from=datetime(2026, 7, 5, 10, 0, 0)) == [
        second
    ]
    assert service.list_defaults(created_to=datetime(2026, 7, 5, 9, 0, 0)) == [first]
    assert service.count_defaults(value_type=SystemSettingValueType.BOOLEAN.value) == 1
    assert service.count_setting_defaults(category="security") == 1
    assert service.count_defaults(status=SystemSettingDefaultStatus.INACTIVE.value) == 1
    assert service.count_defaults(key="missing") == 0

    updated = service.update_default(
        first.id,
        {
            "default_value": {"minLength": 16},
            "metadata_json": {"source": "policy", "nested": {"version": 2}},
        },
    )

    assert updated is first
    assert first.default_value == {"minLength": 16}
    assert first.metadata_json == {"source": "policy", "nested": {"version": 2}}
    assert service.update_default(999, {"title": "Missing"}) is None
    with pytest.raises(
        ValueError,
        match="Unsupported system setting default update fields: id",
    ):
        service.update_default(first.id, {"id": 999})


def test_system_settings_service_change_events_create_lookup_and_filters(
    service: SystemSettingsService,
    db_session: Session,
) -> None:
    actor = create_test_user(db_session, "system-settings-service-actor")
    setting = create_setting(service)
    first = service.create_change_event(
        SystemSettingChangeEvent(
            system_setting_id=setting.id,
            category=setting.category,
            key=setting.key,
            action=SystemSettingChangeAction.CREATED.value,
            old_value=None,
            new_value={"minLength": 12},
            actor_user_id=actor.id,
            source="admin-ui",
            request_id="req-1",
            correlation_id="corr-1",
            metadata_json={"ip": "127.0.0.1"},
            created_at=datetime(2026, 7, 5, 9, 0, 0),
        )
    )
    second = service.create_event(
        {
            "system_setting_id": setting.id,
            "category": setting.category,
            "key": setting.key,
            "action": SystemSettingChangeAction.UPDATED.value,
            "old_value": {"minLength": 12},
            "new_value": {"minLength": 14},
            "actor_user_id": actor.id,
            "source": "api",
            "request_id": "req-2",
            "correlation_id": "corr-2",
            "metadata_json": {"reason": "hardening"},
            "created_at": datetime(2026, 7, 5, 10, 0, 0),
        }
    )

    assert service.get_change_event(first.id) == first
    assert service.get_change_event_by_id(first.id) == first
    assert service.get_change_event_by_uuid(first.event_uuid) == first
    assert service.get_event_by_uuid(second.event_uuid) == second
    assert service.get_change_event(999) is None
    assert service.get_change_event_by_uuid(uuid4()) is None
    assert service.change_event_exists(first.id) is True
    assert service.change_event_exists(999) is False
    assert service.list_change_events(system_setting_id=setting.id) == [second, first]
    assert service.list_change_events(limit=1) == [second]
    assert service.list_change_events(offset=1, limit=1) == [first]
    assert service.list_events(action=SystemSettingChangeAction.CREATED.value) == [
        first
    ]
    assert service.list_change_events(actor_user_id=actor.id) == [second, first]
    assert service.list_change_events(source="api") == [second]
    assert service.list_change_events(request_id="req-1") == [first]
    assert service.list_change_events(correlation_id="corr-2") == [second]
    assert service.list_change_events(
        created_from=datetime(2026, 7, 5, 10, 0, 0),
    ) == [second]
    assert service.list_change_events(created_to=datetime(2026, 7, 5, 9, 0, 0)) == [
        first
    ]
    assert service.count_change_events(category=setting.category) == 2
    assert service.count_events(source="api") == 1
    assert service.count_change_events(actor_user_id=actor.id) == 2
    assert service.count_change_events(request_id="missing") == 0
    assert first.metadata_json == {"ip": "127.0.0.1"}
    assert second.new_value == {"minLength": 14}


def test_system_settings_service_aggregate_repository_consistency(
    service: SystemSettingsService,
    db_session: Session,
) -> None:
    setting = create_setting(service)
    default = service.create_setting_default(
        {
            "category": setting.category,
            "key": "session_timeout",
            "title": "Session timeout",
            "default_value": 30,
            "value_type": SystemSettingValueType.INTEGER.value,
        }
    )
    event = service.create_event(
        {
            "system_setting_id": setting.id,
            "category": setting.category,
            "key": setting.key,
            "action": SystemSettingChangeAction.CREATED.value,
        }
    )

    assert service.repository.db is db_session
    assert service.health() == {
        "module": "system_settings",
        "status": "ok",
        "repositories": {
            "settings": True,
            "defaults": True,
            "change_events": True,
        },
    }
    assert service.get_system_setting(setting.id) == setting
    assert service.get_setting_default(default.id) == default
    assert service.get_event(event.id) == event
    assert event.system_setting_id == setting.id
    assert event.event_uuid != setting.uuid
