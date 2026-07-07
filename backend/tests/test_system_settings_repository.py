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
    SystemSettingDefault,
    SystemSettingDefaultStatus,
    SystemSettingStatus,
    SystemSettingValueType,
)
from app.modules.system_settings.repository import (
    SystemSettingChangeEventRepository,
    SystemSettingDefaultRepository,
    SystemSettingRepository,
    SystemSettingsRepository,
)


def create_test_user(
    db_session: Session,
    username: str = "system-settings-repository-user",
) -> User:
    user = User(
        username=username,
        full_name="System Settings Repository User",
        password_hash="not-used",
        role="test",
        is_active=True,
    )
    db_session.add(user)
    db_session.flush()
    return user


def create_setting(
    repository: SystemSettingRepository,
    *,
    category: str = "security",
    key: str = "password_policy",
    title: str = "Password policy",
    description: str | None = "Rules for account passwords",
    value: dict[str, object] | list[object] | str | int | float | bool | None = None,
    default_value: dict[str, object] | list[object] | str | int | float | bool | None = None,
    value_type: str = SystemSettingValueType.OBJECT.value,
    validation_rules: dict[str, object] | None = None,
    metadata_json: dict[str, object] | None = None,
    status: str = SystemSettingStatus.ACTIVE.value,
    created_by_id: int | None = None,
    updated_by_id: int | None = None,
    created_at: datetime | None = None,
) -> SystemSetting:
    return repository.create(
        SystemSetting(
            category=category,
            key=key,
            title=title,
            description=description,
            value=value
            if value is not None
            else {"minLength": 12, "classes": ["upper", "digit"]},
            default_value=default_value if default_value is not None else {"minLength": 10},
            value_type=value_type,
            validation_rules=validation_rules
            if validation_rules is not None
            else {"required": ["minLength"]},
            metadata_json=metadata_json
            if metadata_json is not None
            else {"scope": "global", "labels": ["auth"]},
            status=status,
            created_by_id=created_by_id,
            updated_by_id=updated_by_id,
            created_at=created_at,
        ),
    )


def create_default(
    repository: SystemSettingDefaultRepository,
    *,
    category: str = "security",
    key: str = "password_policy",
    title: str = "Default password policy",
    description: str | None = "Baseline password rules",
    default_value: dict[str, object] | list[object] | str | int | float | bool | None = None,
    value_type: str = SystemSettingValueType.OBJECT.value,
    validation_rules: dict[str, object] | None = None,
    metadata_json: dict[str, object] | None = None,
    status: str = SystemSettingDefaultStatus.ACTIVE.value,
    created_at: datetime | None = None,
) -> SystemSettingDefault:
    return repository.create(
        SystemSettingDefault(
            category=category,
            key=key,
            title=title,
            description=description,
            default_value=default_value if default_value is not None else {"minLength": 12},
            value_type=value_type,
            validation_rules=validation_rules
            if validation_rules is not None
            else {"minimum": 8},
            metadata_json=metadata_json
            if metadata_json is not None
            else {"source": "baseline"},
            status=status,
            created_at=created_at,
        ),
    )


def create_event(
    repository: SystemSettingChangeEventRepository,
    *,
    system_setting_id: int | None = None,
    category: str = "security",
    key: str = "password_policy",
    action: str = SystemSettingChangeAction.CREATED.value,
    old_value: dict[str, object] | list[object] | str | int | float | bool | None = None,
    new_value: dict[str, object] | list[object] | str | int | float | bool | None = None,
    actor_user_id: int | None = None,
    reason: str | None = "Initial configuration",
    source: str | None = "admin-ui",
    request_id: str | None = "request-001",
    correlation_id: str | None = "correlation-001",
    metadata_json: dict[str, object] | None = None,
    created_at: datetime | None = None,
) -> SystemSettingChangeEvent:
    return repository.create(
        SystemSettingChangeEvent(
            system_setting_id=system_setting_id,
            category=category,
            key=key,
            action=action,
            old_value=old_value,
            new_value=new_value if new_value is not None else {"minLength": 12},
            actor_user_id=actor_user_id,
            reason=reason,
            source=source,
            request_id=request_id,
            correlation_id=correlation_id,
            metadata_json=metadata_json
            if metadata_json is not None
            else {"ip": "127.0.0.1", "tags": ["settings"]},
            created_at=created_at,
        ),
    )


def test_setting_repository_create_lookup_update_soft_delete_and_health(
    db_session: Session,
) -> None:
    repository = SystemSettingRepository(db_session)
    creator = create_test_user(db_session)
    updater = create_test_user(db_session, "system-settings-repository-updater")

    setting = create_setting(
        repository,
        created_by_id=creator.id,
        updated_by_id=creator.id,
    )
    alias_setting = repository.create_setting(
        SystemSetting(
            category="notifications",
            key="email_enabled",
            title="Email enabled",
            value=True,
            default_value=False,
            value_type=SystemSettingValueType.BOOLEAN.value,
            status=SystemSettingStatus.DRAFT.value,
            created_by_id=creator.id,
        ),
    )
    original_uuid = setting.uuid

    assert repository.health() is True
    assert setting.id is not None
    assert setting.uuid is not None
    assert setting.created_at is not None
    assert setting.updated_at is not None
    assert alias_setting.id is not None
    assert db_session.get(SystemSetting, setting.id) == setting
    assert repository.get_by_id(setting.id) == setting
    assert repository.get_by_uuid(original_uuid) == setting
    assert repository.get_by_key("security", "password_policy") == setting
    assert repository.exists(setting.id) is True
    assert repository.get_by_id(999) is None
    assert repository.get_by_uuid(uuid4()) is None
    assert repository.get_by_key("missing", "setting") is None
    assert repository.exists(999) is False
    assert setting.value == {"minLength": 12, "classes": ["upper", "digit"]}
    assert setting.default_value == {"minLength": 10}
    assert setting.validation_rules == {"required": ["minLength"]}
    assert setting.metadata_json == {"scope": "global", "labels": ["auth"]}

    updated_setting = repository.update(
        setting.id,
        {
            "title": "Updated password policy",
            "description": "Updated account password rules",
            "value": {"minLength": 14, "classes": ["upper", "digit", "symbol"]},
            "default_value": {"minLength": 12},
            "value_type": SystemSettingValueType.OBJECT.value,
            "validation_rules": {"required": ["minLength", "classes"]},
            "metadata_json": {"scope": "tenant", "flags": {"sensitive": True}},
            "status": SystemSettingStatus.INACTIVE.value,
            "updated_by_id": updater.id,
        },
    )

    assert updated_setting is setting
    assert setting.uuid == original_uuid
    assert repository.get_by_uuid(original_uuid) == setting
    assert setting.title == "Updated password policy"
    assert setting.value == {"minLength": 14, "classes": ["upper", "digit", "symbol"]}
    assert setting.default_value == {"minLength": 12}
    assert setting.validation_rules == {"required": ["minLength", "classes"]}
    assert setting.metadata_json == {"scope": "tenant", "flags": {"sensitive": True}}
    assert setting.status == SystemSettingStatus.INACTIVE.value
    assert setting.updated_by_id == updater.id
    assert repository.update(999, {"title": "Missing"}) is None
    with pytest.raises(ValueError, match="Unsupported system setting update fields: id"):
        repository.update(setting.id, {"id": 999})

    assert repository.mark_deleted(setting.id, deleted_by_id=updater.id) is True
    assert setting.deleted_at is not None
    assert setting.deleted_by_id == updater.id
    assert repository.get_by_id(setting.id) is None
    assert repository.get_by_id(setting.id, include_deleted=True) == setting
    assert repository.get_by_uuid(original_uuid) is None
    assert repository.get_by_uuid(original_uuid, include_deleted=True) == setting
    assert repository.get_by_key("security", "password_policy") is None
    assert (
        repository.get_by_key("security", "password_policy", include_deleted=True)
        == setting
    )
    assert repository.exists(setting.id) is False
    assert repository.exists(setting.id, include_deleted=True) is True
    assert repository.list() == [alias_setting]
    assert repository.count() == 1
    assert repository.list(include_deleted=True) == [alias_setting, setting]
    assert repository.count(include_deleted=True) == 2
    assert repository.delete(999) is False
    assert repository.mark_deleted(999) is False


def test_setting_repository_list_filters_count_ordering_and_pagination(
    db_session: Session,
) -> None:
    repository = SystemSettingRepository(db_session)
    creator = create_test_user(db_session, "system-settings-filter-creator")
    updater = create_test_user(db_session, "system-settings-filter-updater")
    other_creator = create_test_user(db_session, "system-settings-filter-other")

    first = create_setting(
        repository,
        category="security",
        key="password_policy",
        status=SystemSettingStatus.ACTIVE.value,
        value_type=SystemSettingValueType.OBJECT.value,
        created_by_id=creator.id,
        updated_by_id=updater.id,
        created_at=datetime(2026, 7, 5, 9, 0, 0),
    )
    second = create_setting(
        repository,
        category="notifications",
        key="email_enabled",
        title="Email enabled",
        value=True,
        default_value=False,
        value_type=SystemSettingValueType.BOOLEAN.value,
        status=SystemSettingStatus.DRAFT.value,
        created_by_id=creator.id,
        updated_by_id=creator.id,
        created_at=datetime(2026, 7, 5, 10, 0, 0),
    )
    third = create_setting(
        repository,
        category="appearance",
        key="theme",
        title="Theme",
        value="dark",
        default_value="light",
        value_type=SystemSettingValueType.STRING.value,
        status=SystemSettingStatus.ARCHIVED.value,
        created_by_id=other_creator.id,
        updated_by_id=updater.id,
        created_at=datetime(2026, 7, 5, 11, 0, 0),
    )

    assert repository.list() == [third, second, first]
    assert repository.list(limit=2) == [third, second]
    assert repository.list(offset=1, limit=1) == [second]
    assert repository.list(category="security") == [first]
    assert repository.list(key="email_enabled") == [second]
    assert repository.list(status=SystemSettingStatus.ARCHIVED.value) == [third]
    assert repository.list(value_type=SystemSettingValueType.BOOLEAN.value) == [second]
    assert repository.list(created_by_id=creator.id) == [second, first]
    assert repository.list(updated_by_id=updater.id) == [third, first]
    assert repository.list(created_from=datetime(2026, 7, 5, 10, 0, 0)) == [
        third,
        second,
    ]
    assert repository.list(created_to=datetime(2026, 7, 5, 10, 0, 0)) == [
        second,
        first,
    ]
    assert repository.list(category="missing") == []
    assert repository.count() == 3
    assert repository.count(created_by_id=creator.id) == 2
    assert repository.count(status=SystemSettingStatus.ACTIVE.value) == 1
    assert repository.count(
        category="notifications",
        value_type=SystemSettingValueType.BOOLEAN.value,
    ) == 1
    assert repository.count(key="missing") == 0


def test_default_repository_create_lookup_update_filters_and_health(
    db_session: Session,
) -> None:
    repository = SystemSettingDefaultRepository(db_session)

    default = create_default(repository)
    alias_default = repository.create_default(
        SystemSettingDefault(
            category="notifications",
            key="email_enabled",
            title="Email enabled",
            default_value=True,
            value_type=SystemSettingValueType.BOOLEAN.value,
            status=SystemSettingDefaultStatus.INACTIVE.value,
        ),
    )
    original_uuid = default.uuid

    assert repository.health() is True
    assert default.id is not None
    assert default.uuid is not None
    assert default.created_at is not None
    assert default.updated_at is not None
    assert alias_default.id is not None
    assert db_session.get(SystemSettingDefault, default.id) == default
    assert repository.get_by_id(default.id) == default
    assert repository.get_by_uuid(original_uuid) == default
    assert repository.get_by_key("security", "password_policy") == default
    assert repository.exists(default.id) is True
    assert repository.get_by_id(999) is None
    assert repository.get_by_uuid(uuid4()) is None
    assert repository.get_by_key("missing", "setting") is None
    assert repository.exists(999) is False
    assert default.default_value == {"minLength": 12}
    assert default.validation_rules == {"minimum": 8}
    assert default.metadata_json == {"source": "baseline"}

    updated_default = repository.update(
        default.id,
        {
            "title": "Updated default password policy",
            "description": "Updated baseline password rules",
            "default_value": {"minLength": 16},
            "value_type": SystemSettingValueType.OBJECT.value,
            "validation_rules": {"minimum": 12},
            "status": SystemSettingDefaultStatus.DEPRECATED.value,
            "metadata_json": {"source": "policy", "nested": {"version": 2}},
        },
    )

    assert updated_default is default
    assert default.uuid == original_uuid
    assert repository.get_by_uuid(original_uuid) == default
    assert default.title == "Updated default password policy"
    assert default.default_value == {"minLength": 16}
    assert default.validation_rules == {"minimum": 12}
    assert default.status == SystemSettingDefaultStatus.DEPRECATED.value
    assert default.metadata_json == {"source": "policy", "nested": {"version": 2}}
    assert repository.update(999, {"title": "Missing"}) is None
    with pytest.raises(
        ValueError,
        match="Unsupported system setting default update fields: id",
    ):
        repository.update(default.id, {"id": 999})

    assert repository.list() == [alias_default, default]
    assert repository.list(limit=1) == [alias_default]
    assert repository.list(offset=1, limit=1) == [default]
    assert repository.list(category="security") == [default]
    assert repository.list(key="email_enabled") == [alias_default]
    assert repository.list(status=SystemSettingDefaultStatus.INACTIVE.value) == [
        alias_default
    ]
    assert repository.list(value_type=SystemSettingValueType.OBJECT.value) == [
        default
    ]
    assert repository.count() == 2
    assert repository.count(category="security") == 1
    assert repository.count(value_type=SystemSettingValueType.BOOLEAN.value) == 1
    assert repository.count(key="missing") == 0


def test_default_repository_date_filters_and_ordering(
    db_session: Session,
) -> None:
    repository = SystemSettingDefaultRepository(db_session)

    first = create_default(
        repository,
        category="security",
        key="password_policy",
        created_at=datetime(2026, 7, 5, 9, 0, 0),
    )
    second = create_default(
        repository,
        category="notifications",
        key="email_enabled",
        title="Email enabled",
        default_value=True,
        value_type=SystemSettingValueType.BOOLEAN.value,
        created_at=datetime(2026, 7, 5, 10, 0, 0),
    )
    third = create_default(
        repository,
        category="appearance",
        key="theme",
        title="Theme",
        default_value="light",
        value_type=SystemSettingValueType.STRING.value,
        status=SystemSettingDefaultStatus.DEPRECATED.value,
        created_at=datetime(2026, 7, 5, 11, 0, 0),
    )

    assert repository.list() == [third, second, first]
    assert repository.list(created_from=datetime(2026, 7, 5, 10, 0, 0)) == [
        third,
        second,
    ]
    assert repository.list(created_to=datetime(2026, 7, 5, 10, 0, 0)) == [
        second,
        first,
    ]
    assert repository.count(created_from=datetime(2026, 7, 5, 10, 0, 0)) == 2
    assert repository.count(
        status=SystemSettingDefaultStatus.DEPRECATED.value,
        created_to=datetime(2026, 7, 5, 11, 0, 0),
    ) == 1


def test_change_event_repository_create_lookup_filters_count_and_health(
    db_session: Session,
) -> None:
    setting_repository = SystemSettingRepository(db_session)
    event_repository = SystemSettingChangeEventRepository(db_session)
    actor = create_test_user(db_session, "system-settings-event-actor")
    setting = create_setting(setting_repository, created_by_id=actor.id)

    first = create_event(
        event_repository,
        system_setting_id=setting.id,
        category=setting.category,
        key=setting.key,
        action=SystemSettingChangeAction.CREATED.value,
        actor_user_id=actor.id,
        source="admin-ui",
        request_id="request-001",
        correlation_id="correlation-001",
        created_at=datetime(2026, 7, 5, 9, 0, 0),
    )
    second = event_repository.create_event(
        SystemSettingChangeEvent(
            system_setting_id=setting.id,
            category=setting.category,
            key=setting.key,
            action=SystemSettingChangeAction.UPDATED.value,
            old_value={"minLength": 12},
            new_value={"minLength": 14},
            actor_user_id=actor.id,
            reason="Hardening policy",
            source="api",
            request_id="request-002",
            correlation_id="correlation-002",
            metadata_json={"reason": "hardening"},
            created_at=datetime(2026, 7, 5, 10, 0, 0),
        ),
    )
    third = create_event(
        event_repository,
        system_setting_id=None,
        category="notifications",
        key="email_enabled",
        action=SystemSettingChangeAction.DEFAULT_APPLIED.value,
        old_value=False,
        new_value=True,
        actor_user_id=None,
        source="seed",
        request_id="request-003",
        correlation_id="correlation-003",
        created_at=datetime(2026, 7, 5, 11, 0, 0),
    )
    original_uuid = first.event_uuid

    assert event_repository.health() is True
    assert first.id is not None
    assert first.event_uuid is not None
    assert first.created_at is not None
    assert db_session.get(SystemSettingChangeEvent, first.id) == first
    assert event_repository.get_by_id(first.id) == first
    assert event_repository.get_by_uuid(original_uuid) == first
    assert event_repository.exists(first.id) is True
    assert event_repository.get_by_id(999) is None
    assert event_repository.get_by_uuid(uuid4()) is None
    assert event_repository.exists(999) is False
    assert first.old_value is None
    assert first.new_value == {"minLength": 12}
    assert first.metadata_json == {"ip": "127.0.0.1", "tags": ["settings"]}
    assert second.old_value == {"minLength": 12}
    assert second.new_value == {"minLength": 14}
    assert second.metadata_json == {"reason": "hardening"}

    assert event_repository.list() == [third, second, first]
    assert event_repository.list(limit=2) == [third, second]
    assert event_repository.list(offset=1, limit=1) == [second]
    assert event_repository.list(system_setting_id=setting.id) == [second, first]
    assert event_repository.list(category="security") == [second, first]
    assert event_repository.list(key="email_enabled") == [third]
    assert event_repository.list(action=SystemSettingChangeAction.CREATED.value) == [
        first
    ]
    assert event_repository.list(actor_user_id=actor.id) == [second, first]
    assert event_repository.list(source="seed") == [third]
    assert event_repository.list(request_id="request-002") == [second]
    assert event_repository.list(correlation_id="correlation-003") == [third]
    assert event_repository.list(created_from=datetime(2026, 7, 5, 10, 0, 0)) == [
        third,
        second,
    ]
    assert event_repository.list(created_to=datetime(2026, 7, 5, 10, 0, 0)) == [
        second,
        first,
    ]
    assert event_repository.list(source="missing") == []

    assert event_repository.count() == 3
    assert event_repository.count(system_setting_id=setting.id) == 2
    assert event_repository.count(category="security") == 2
    assert event_repository.count(action=SystemSettingChangeAction.UPDATED.value) == 1
    assert event_repository.count(actor_user_id=actor.id) == 2
    assert event_repository.count(source="api") == 1
    assert event_repository.count(request_id="missing") == 0


def test_aggregate_repository_exposes_boundaries_and_health(
    db_session: Session,
) -> None:
    repository = SystemSettingsRepository(db_session)

    setting = create_setting(repository.settings)
    default = create_default(
        repository.defaults,
        category=setting.category,
        key="session_timeout",
        title="Session timeout",
        default_value=30,
        value_type=SystemSettingValueType.INTEGER.value,
    )
    event = create_event(
        repository.change_events,
        system_setting_id=setting.id,
        category=setting.category,
        key=setting.key,
    )

    assert repository.db is db_session
    assert isinstance(repository.settings, SystemSettingRepository)
    assert isinstance(repository.defaults, SystemSettingDefaultRepository)
    assert isinstance(repository.change_events, SystemSettingChangeEventRepository)
    assert repository.health() is True
    assert repository.health_check() is True
    assert repository.settings.get_by_id(setting.id) == setting
    assert repository.defaults.get_by_id(default.id) == default
    assert repository.change_events.get_by_id(event.id) == event
    assert event.system_setting_id == setting.id
    assert event.event_uuid != setting.uuid
