from __future__ import annotations

from datetime import datetime
from uuid import uuid4

import pytest
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.modules.monitoring_health.models import (
    HealthCheckRecord,
    HealthCheckStatus,
    MonitoringMetric,
    MonitoringMetricCategory,
    SystemIncident,
    SystemIncidentSeverity,
    SystemIncidentStatus,
)
from app.modules.monitoring_health.repository import (
    HealthCheckRecordRepository,
    MonitoringHealthRepository,
    MonitoringMetricRepository,
    SystemIncidentRepository,
)


def create_health_check(
    repository: HealthCheckRecordRepository,
    *,
    component: str = "database",
    status: str = HealthCheckStatus.HEALTHY.value,
    checked_at: datetime = datetime(2026, 7, 9, 9, 0),
    created_at: datetime = datetime(2026, 7, 9, 9, 0),
) -> HealthCheckRecord:
    return repository.create(
        HealthCheckRecord(
            component=component,
            status=status,
            response_time_ms=12.5,
            message=f"{component} operational",
            details={"region": "primary", "attempt": 1},
            checked_at=checked_at,
            created_at=created_at,
        )
    )


def create_metric(
    repository: MonitoringMetricRepository,
    *,
    metric_name: str = "cpu.usage",
    category: str = MonitoringMetricCategory.SYSTEM.value,
    source: str | None = "node-a",
    unit: str | None = "percent",
    recorded_at: datetime = datetime(2026, 7, 9, 9, 0),
    created_at: datetime = datetime(2026, 7, 9, 9, 0),
) -> MonitoringMetric:
    return repository.create(
        MonitoringMetric(
            metric_name=metric_name,
            category=category,
            source=source,
            value=42.5,
            unit=unit,
            labels={"host": "node-a"},
            details={"sample": "one"},
            recorded_at=recorded_at,
            created_at=created_at,
        )
    )


def create_incident(
    repository: SystemIncidentRepository,
    *,
    title: str = "Database latency",
    severity: str = SystemIncidentSeverity.HIGH.value,
    status: str = SystemIncidentStatus.OPEN.value,
    source: str | None = "monitor",
    component: str | None = "database",
    detected_at: datetime = datetime(2026, 7, 9, 9, 0),
    resolved_at: datetime | None = None,
    created_at: datetime = datetime(2026, 7, 9, 9, 0),
) -> SystemIncident:
    return repository.create(
        SystemIncident(
            title=title,
            severity=severity,
            status=status,
            source=source,
            component=component,
            description=f"Investigating {title.lower()}",
            resolution_summary=None,
            metadata_json={"ticket": "OPS-15"},
            detected_at=detected_at,
            resolved_at=resolved_at,
            created_at=created_at,
        )
    )


def test_health_check_create_lookup_update_latest_and_health(db_session: Session) -> None:
    repository = HealthCheckRecordRepository(db_session)
    record = create_health_check(repository)
    alias = repository.create_record(
        HealthCheckRecord(component="api", checked_at=datetime(2026, 7, 9, 10, 0))
    )
    latest = create_health_check(
        repository,
        status=HealthCheckStatus.DEGRADED.value,
        checked_at=datetime(2026, 7, 9, 11, 0),
        created_at=datetime(2026, 7, 9, 11, 0),
    )
    original_uuid = record.record_uuid

    assert repository.health() is True
    assert record.id is not None and record.record_uuid is not None
    assert record.created_at is not None and alias.id is not None
    assert alias.status == HealthCheckStatus.UNKNOWN.value
    assert alias.created_at is not None
    assert db_session.scalar(select(HealthCheckRecord).where(HealthCheckRecord.id == record.id)) is record
    assert repository.get_by_id(record.id) is record
    assert repository.get_by_uuid(original_uuid) is record
    assert repository.get_latest_for_component("database") is latest
    assert repository.get_latest_for_component("missing") is None
    assert repository.get_by_id(999) is None
    assert repository.get_by_uuid(uuid4()) is None
    assert repository.exists(record.id) is True
    assert repository.exists(999) is False

    updated = repository.update(
        record.id,
        {"status": HealthCheckStatus.UNHEALTHY.value, "response_time_ms": 88.0,
         "message": "connection refused", "details": {"attempt": 2}},
    )
    db_session.expire(record)
    assert updated is record
    assert record.record_uuid == original_uuid
    assert record.component == "database"
    assert record.status == HealthCheckStatus.UNHEALTHY.value
    assert record.response_time_ms == 88.0
    assert record.message == "connection refused"
    assert record.details == {"attempt": 2}
    assert repository.update(record.id, {"message": None, "details": None}) is record
    db_session.expire(record)
    persisted_record = repository.get_by_id(record.id)
    assert persisted_record is record
    assert persisted_record.message is None
    assert persisted_record.details is None

    assert repository.update(999, {"message": "missing"}) is None
    with pytest.raises(ValueError, match="Unsupported health check record update fields: id"):
        repository.update(record.id, {"id": 999})
    replacement_uuid = uuid4()
    with pytest.raises(ValueError):
        repository.update(record.id, {"record_uuid": replacement_uuid})
    assert record.record_uuid == original_uuid
    assert repository.get_by_uuid(original_uuid) is record
    assert repository.get_by_uuid(replacement_uuid) is None


def test_health_check_list_count_filters_ordering_and_pagination(db_session: Session) -> None:
    repository = HealthCheckRecordRepository(db_session)
    assert repository.list() == [] and repository.count() == 0
    first = create_health_check(repository)
    second = create_health_check(
        repository, component="api", status=HealthCheckStatus.DEGRADED.value,
        checked_at=datetime(2026, 7, 9, 10, 0), created_at=datetime(2026, 7, 9, 10, 0),
    )
    third = create_health_check(
        repository, component="worker", status=HealthCheckStatus.UNHEALTHY.value,
        checked_at=datetime(2026, 7, 9, 11, 0), created_at=datetime(2026, 7, 9, 11, 0),
    )

    assert repository.list() == [third, second, first]
    assert repository.list(limit=2) == [third, second]
    assert repository.list(offset=1) == [second, first]
    assert repository.list(offset=1, limit=1) == [second]
    checks = [
        ({"component": "api"}, [second]),
        ({"status": HealthCheckStatus.UNHEALTHY}, [third]),
        ({"checked_from": datetime(2026, 7, 9, 10, 0)}, [third, second]),
        ({"checked_to": datetime(2026, 7, 9, 10, 0)}, [second, first]),
        ({"created_from": datetime(2026, 7, 9, 10, 0)}, [third, second]),
        ({"created_to": datetime(2026, 7, 9, 10, 0)}, [second, first]),
        ({"search": "WORKER"}, [third]),
        ({"search": "operational"}, [third, second, first]),
        ({"component": "api", "status": HealthCheckStatus.DEGRADED}, [second]),
    ]
    for filters, expected in checks:
        assert repository.list(**filters) == expected
        assert repository.count(**filters) == len(expected)
    assert repository.count() == 3


def test_metric_create_lookup_update_latest_and_health(db_session: Session) -> None:
    repository = MonitoringMetricRepository(db_session)
    metric = create_metric(repository)
    alias = repository.create_metric(MonitoringMetric(metric_name="requests", value=1.0))
    latest = create_metric(
        repository, recorded_at=datetime(2026, 7, 9, 11, 0),
        created_at=datetime(2026, 7, 9, 11, 0),
    )
    original_uuid = metric.metric_uuid

    assert repository.health() is True
    assert metric.id is not None and metric.metric_uuid is not None
    assert metric.created_at is not None and alias.id is not None
    assert alias.category == MonitoringMetricCategory.CUSTOM.value
    assert alias.recorded_at is not None and alias.created_at is not None
    assert db_session.get(MonitoringMetric, metric.id) is metric
    assert repository.get_by_id(metric.id) is metric
    assert repository.get_by_uuid(original_uuid) is metric
    assert repository.get_latest_by_name("cpu.usage") is latest
    assert repository.get_latest_by_name("cpu.usage", source="node-a") is latest
    assert repository.get_latest_by_name("cpu.usage", source="missing") is None
    assert repository.get_by_id(999) is None
    assert repository.get_by_uuid(uuid4()) is None
    assert repository.exists(metric.id) is True and repository.exists(999) is False

    updated = repository.update(
        metric.id,
        {"value": 75.0, "unit": "pct", "labels": {"host": "node-b"},
         "details": {"sample": "updated"}},
    )
    db_session.expire(metric)
    assert updated is metric and metric.metric_uuid == original_uuid
    assert metric.metric_name == "cpu.usage" and metric.value == 75.0
    assert metric.unit == "pct" and metric.labels == {"host": "node-b"}
    assert metric.details == {"sample": "updated"}
    assert repository.update(999, {"value": 0.0}) is None
    with pytest.raises(ValueError, match="Unsupported monitoring metric update fields: id"):
        repository.update(metric.id, {"id": 999})
    replacement_uuid = uuid4()
    with pytest.raises(ValueError):
        repository.update(metric.id, {"metric_uuid": replacement_uuid})
    assert metric.metric_uuid == original_uuid
    assert repository.get_by_uuid(original_uuid) is metric
    assert repository.get_by_uuid(replacement_uuid) is None


def test_metric_list_count_filters_ordering_and_pagination(db_session: Session) -> None:
    repository = MonitoringMetricRepository(db_session)
    assert repository.list() == [] and repository.count() == 0
    first = create_metric(repository)
    second = create_metric(
        repository, metric_name="request.duration", category=MonitoringMetricCategory.APPLICATION.value,
        source="api", unit="ms", recorded_at=datetime(2026, 7, 9, 10, 0),
        created_at=datetime(2026, 7, 9, 10, 0),
    )
    third = create_metric(
        repository, metric_name="connections", category=MonitoringMetricCategory.DATABASE.value,
        source="postgres", unit="count", recorded_at=datetime(2026, 7, 9, 11, 0),
        created_at=datetime(2026, 7, 9, 11, 0),
    )

    assert repository.list() == [third, second, first]
    assert repository.list(limit=2) == [third, second]
    assert repository.list(offset=1, limit=1) == [second]
    checks = [
        ({"metric_name": "request.duration"}, [second]),
        ({"category": MonitoringMetricCategory.DATABASE}, [third]),
        ({"source": "api"}, [second]), ({"unit": "percent"}, [first]),
        ({"recorded_from": datetime(2026, 7, 9, 10, 0)}, [third, second]),
        ({"recorded_to": datetime(2026, 7, 9, 10, 0)}, [second, first]),
        ({"created_from": datetime(2026, 7, 9, 10, 0)}, [third, second]),
        ({"created_to": datetime(2026, 7, 9, 10, 0)}, [second, first]),
        ({"search": "REQUEST"}, [second]), ({"search": "postgres"}, [third]),
        ({"category": MonitoringMetricCategory.APPLICATION, "source": "api", "unit": "ms"}, [second]),
    ]
    for filters, expected in checks:
        assert repository.list(**filters) == expected
        assert repository.count(**filters) == len(expected)
    assert repository.count() == 3


def test_incident_create_lookup_update_and_health(db_session: Session) -> None:
    repository = SystemIncidentRepository(db_session)
    incident = create_incident(repository)
    alias = repository.create_incident(SystemIncident(title="Default incident"))
    original_uuid = incident.incident_uuid

    assert repository.health() is True
    assert incident.id is not None and incident.incident_uuid is not None
    assert incident.created_at is not None and incident.updated_at is not None
    assert alias.id is not None
    assert alias.severity == SystemIncidentSeverity.MEDIUM.value
    assert alias.status == SystemIncidentStatus.OPEN.value
    assert alias.detected_at is not None and alias.updated_at is not None
    assert db_session.get(SystemIncident, incident.id) is incident
    assert repository.get_by_id(incident.id) is incident
    assert repository.get_by_uuid(original_uuid) is incident
    assert repository.get_by_id(999) is None
    assert repository.get_by_uuid(uuid4()) is None
    assert repository.exists(incident.id) is True and repository.exists(999) is False

    resolved_at = datetime(2026, 7, 9, 12, 0)
    updated = repository.update(
        incident.id,
        {"status": SystemIncidentStatus.RESOLVED.value, "resolution_summary": "Pool resized",
         "resolved_at": resolved_at, "metadata_json": {"ticket": "OPS-15", "fixed": True}},
    )
    db_session.expire(incident)
    assert updated is incident and incident.incident_uuid == original_uuid
    assert incident.title == "Database latency" and incident.severity == SystemIncidentSeverity.HIGH.value
    assert incident.status == SystemIncidentStatus.RESOLVED.value
    assert incident.resolution_summary == "Pool resized" and incident.resolved_at == resolved_at
    assert incident.metadata_json == {"ticket": "OPS-15", "fixed": True}
    assert incident.updated_at is not None

    assert repository.update(
        incident.id,
        {"resolution_summary": None, "metadata_json": None},
    ) is incident
    db_session.expire(incident)
    persisted_incident = repository.get_by_id(incident.id)
    assert persisted_incident is incident
    assert persisted_incident.resolution_summary is None
    assert persisted_incident.metadata_json is None

    assert repository.update(999, {"status": SystemIncidentStatus.CLOSED.value}) is None
    with pytest.raises(ValueError, match="Unsupported system incident update fields: id"):
        repository.update(incident.id, {"id": 999})
    replacement_uuid = uuid4()
    with pytest.raises(ValueError):
        repository.update(incident.id, {"incident_uuid": replacement_uuid})
    assert incident.incident_uuid == original_uuid
    assert repository.get_by_uuid(original_uuid) is incident
    assert repository.get_by_uuid(replacement_uuid) is None


def test_incident_list_count_filters_ordering_and_pagination(db_session: Session) -> None:
    repository = SystemIncidentRepository(db_session)
    assert repository.list() == [] and repository.count() == 0
    first = create_incident(repository)
    second = create_incident(
        repository, title="API errors", severity=SystemIncidentSeverity.MEDIUM.value,
        status=SystemIncidentStatus.INVESTIGATING.value, source="apm", component="api",
        detected_at=datetime(2026, 7, 9, 10, 0), created_at=datetime(2026, 7, 9, 10, 0),
    )
    third = create_incident(
        repository, title="Worker recovered", severity=SystemIncidentSeverity.LOW.value,
        status=SystemIncidentStatus.RESOLVED.value, source="scheduler", component="worker",
        detected_at=datetime(2026, 7, 9, 11, 0), resolved_at=datetime(2026, 7, 9, 12, 0),
        created_at=datetime(2026, 7, 9, 11, 0),
    )
    third.resolution_summary = "Restart completed"
    db_session.flush()

    assert repository.list() == [third, second, first]
    assert repository.list(limit=2) == [third, second]
    assert repository.list(offset=1, limit=1) == [second]
    checks = [
        ({"title": "API errors"}, [second]),
        ({"severity": SystemIncidentSeverity.LOW}, [third]),
        ({"status": SystemIncidentStatus.INVESTIGATING}, [second]),
        ({"source": "monitor"}, [first]), ({"component": "api"}, [second]),
        ({"detected_from": datetime(2026, 7, 9, 10, 0)}, [third, second]),
        ({"detected_to": datetime(2026, 7, 9, 10, 0)}, [second, first]),
        ({"resolved_from": datetime(2026, 7, 9, 12, 0)}, [third]),
        ({"resolved_to": datetime(2026, 7, 9, 12, 0)}, [third]),
        ({"created_from": datetime(2026, 7, 9, 10, 0)}, [third, second]),
        ({"created_to": datetime(2026, 7, 9, 10, 0)}, [second, first]),
        ({"search": "WORKER"}, [third]), ({"search": "restart"}, [third]),
        ({"severity": SystemIncidentSeverity.MEDIUM, "status": SystemIncidentStatus.INVESTIGATING,
          "source": "apm", "component": "api"}, [second]),
    ]
    for filters, expected in checks:
        assert repository.list(**filters) == expected
        assert repository.count(**filters) == len(expected)
    assert repository.count() == 3


@pytest.mark.parametrize(
    ("model", "uuid_field", "required_values"),
    [
        (HealthCheckRecord, "record_uuid", {"component": "api"}),
        (MonitoringMetric, "metric_uuid", {"metric_name": "latency", "value": 1.0}),
        (SystemIncident, "incident_uuid", {"title": "Failure"}),
    ],
)
def test_unique_uuid_constraints(
    db_session: Session, model: type[object], uuid_field: str, required_values: dict[str, object]
) -> None:
    duplicate_uuid = uuid4()
    db_session.add(model(**required_values, **{uuid_field: duplicate_uuid}))
    db_session.flush()
    db_session.add(model(**required_values, **{uuid_field: duplicate_uuid}))
    with pytest.raises(IntegrityError):
        db_session.flush()
    db_session.rollback()


@pytest.mark.parametrize(
    "model",
    [HealthCheckRecord(component=None), MonitoringMetric(metric_name=None, value=1.0), SystemIncident(title=None)],
)
def test_required_business_fields_are_not_nullable(db_session: Session, model: object) -> None:
    db_session.add(model)
    with pytest.raises(IntegrityError):
        db_session.flush()
    db_session.rollback()


def test_aggregate_repository_exposes_boundaries_and_health(db_session: Session) -> None:
    repository = MonitoringHealthRepository(db_session)
    health_check = create_health_check(repository.health_checks)
    metric = create_metric(repository.metrics)
    incident = create_incident(repository.incidents)

    assert repository.db is db_session
    assert isinstance(repository.health_checks, HealthCheckRecordRepository)
    assert isinstance(repository.metrics, MonitoringMetricRepository)
    assert isinstance(repository.incidents, SystemIncidentRepository)
    assert repository.health() is True and repository.health_check() is True
    assert repository.health_checks.get_by_id(health_check.id) is health_check
    assert repository.metrics.get_by_id(metric.id) is metric
    assert repository.incidents.get_by_id(incident.id) is incident
    assert repository.health_checks.get_by_uuid(metric.metric_uuid) is None
    assert repository.metrics.get_by_uuid(incident.incident_uuid) is None
    assert repository.incidents.get_by_uuid(health_check.record_uuid) is None

