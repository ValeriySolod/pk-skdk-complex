from __future__ import annotations

from datetime import datetime, timedelta, timezone
from uuid import uuid4

import pytest
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
from app.modules.monitoring_health.repository import MonitoringHealthRepository
from app.modules.monitoring_health.service import MonitoringHealthService


@pytest.fixture()
def service(db_session: Session) -> MonitoringHealthService:
    return MonitoringHealthService(MonitoringHealthRepository(db_session))


def test_health_check_create_get_list_count_and_latest(
    service: MonitoringHealthService,
) -> None:
    earlier = datetime.now(timezone.utc) - timedelta(minutes=1)
    first = service.create_health_check(
        {"component": "database", "status": "healthy", "checked_at": earlier}
    )
    latest = service.create_health_check(
        {"component": "database", "status": "degraded", "message": "slow"}
    )

    assert service.get_health_check(first.id) is first
    assert service.get_health_check_by_uuid(latest.record_uuid) is latest
    assert service.get_latest_health_check("database") is latest
    assert service.list_health_checks(
        component="database", status="degraded", limit=1, offset=0
    ) == [latest]
    assert service.count_health_checks(component="database") == 2
    assert service.get_health_check_by_uuid(uuid4()) is None


def test_metric_create_get_list_count_and_latest(
    service: MonitoringHealthService,
) -> None:
    service.create_metric(
        {"metric_name": "cpu.load", "category": "system", "source": "node-1", "value": 0.25}
    )
    latest = service.create_metric(
        {"metric_name": "cpu.load", "category": "system", "source": "node-1", "value": 0.75}
    )

    assert service.get_metric(latest.id) is latest
    assert service.get_metric_by_uuid(latest.metric_uuid) is latest
    assert service.get_latest_metric("cpu.load", source="node-1") is latest
    assert service.list_metrics(category="system", source="node-1", limit=1, offset=0) == [latest]
    assert service.count_metrics(metric_name="cpu.load", source="node-1") == 2
    assert service.get_metric_by_uuid(uuid4()) is None


def test_incident_crud_and_lifecycle_rules(service: MonitoringHealthService) -> None:
    incident = service.create_incident(
        {"title": "Database latency", "severity": "high", "component": "database"}
    )
    assert service.get_incident_by_uuid(incident.incident_uuid) is incident
    assert service.list_incidents(status="open", limit=10, offset=0) == [incident]
    assert service.count_incidents(component="database") == 1

    service.mark_incident_status(
        incident.id, SystemIncidentStatus.RESOLVED,
        resolution_summary="Query plan corrected",
    )
    assert incident.resolved_at is not None
    service.mark_incident_status(incident.id, "investigating")
    assert incident.resolved_at is None
    assert service.update_incident(incident.id, {"severity": "critical"}) is incident
    assert service.update_incident(999_999, {"severity": "low"}) is None

    with pytest.raises(ValueError, match="resolved_at is only valid"):
        service.update_incident(incident.id, {"resolved_at": datetime.now(timezone.utc)})
    with pytest.raises(ValueError, match="resolution_summary must not be empty"):
        service.mark_incident_status(incident.id, "resolved", resolution_summary="   ")


@pytest.mark.parametrize("terminal_status", ["resolved", "closed"])
def test_update_incident_reopens_terminal_incident_and_clears_resolved_at(
    service: MonitoringHealthService,
    terminal_status: str,
) -> None:
    incident = service.create_incident({"title": "Service interruption"})
    service.mark_incident_status(
        incident.id,
        terminal_status,
        resolution_summary="Service restored",
    )
    stale_resolved_at = incident.resolved_at
    assert stale_resolved_at is not None

    reopened = service.update_incident(
        incident.id,
        {
            "status": "investigating",
            "resolved_at": stale_resolved_at,
        },
    )

    assert reopened is incident
    assert incident.status == "investigating"
    assert incident.resolved_at is None
    assert incident.resolution_summary == "Service restored"


def test_update_incident_resolution_validation_and_terminal_update(
    service: MonitoringHealthService,
) -> None:
    incident = service.create_incident({"title": "Worker failure"})
    resolved_at = datetime.now(timezone.utc)

    terminal = service.update_incident(
        incident.id,
        {
            "status": "resolved",
            "resolved_at": resolved_at,
            "resolution_summary": "Worker restarted",
        },
    )
    assert terminal is incident
    assert incident.resolved_at == resolved_at

    reopened = service.update_incident(incident.id, {"status": "open"})
    assert reopened is incident
    assert incident.resolved_at is None

    with pytest.raises(ValueError, match="resolved_at is only valid"):
        service.update_incident(
            incident.id,
            {"resolved_at": datetime.now(timezone.utc)},
        )
    with pytest.raises(ValueError, match="resolution_summary must not be empty"):
        service.update_incident(incident.id, {"resolution_summary": " "})

    assert service.update_incident(999_999, {"status": "open"}) is None


def test_validation_and_health(service: MonitoringHealthService) -> None:
    with pytest.raises(ValueError, match="Invalid health check status"):
        service.create_health_check({"component": "api", "status": "bad"})
    with pytest.raises(ValueError, match="Invalid metric category"):
        service.create_metric({"metric_name": "requests", "category": "bad", "value": 1})
    with pytest.raises(ValueError, match="Invalid incident severity"):
        service.create_incident({"title": "Incident", "severity": "bad"})
    with pytest.raises(ValueError, match="limit must be greater than zero"):
        service.list_health_checks(limit=0)
    with pytest.raises(ValueError, match="offset must be greater than or equal to zero"):
        service.list_metrics(offset=-1)
    now = datetime.now(timezone.utc)
    with pytest.raises(ValueError, match="checked_from"):
        service.list_health_checks(checked_from=now, checked_to=now - timedelta(seconds=1))

    assert service.health().model_dump() == {"status": "ok", "module": "monitoring_health"}
    assert service.get_module_status()["repositories"] == {
        "health_checks": True, "metrics": True, "incidents": True,
    }


def test_health_check_filters_ordering_pagination_updates_and_json(
    service: MonitoringHealthService,
) -> None:
    base = datetime(2026, 7, 10, 8, 0, tzinfo=timezone.utc)
    first = service.create_health_check(HealthCheckRecord(
        component="api", status=HealthCheckStatus.HEALTHY.value,
        response_time_ms=12.5, details={"region": "eu", "attempts": [1]},
        checked_at=base, created_at=base,
    ))
    second = service.create_health_check({
        "component": "worker", "status": "unhealthy", "message": "Queue stalled",
        "checked_at": base + timedelta(hours=1), "created_at": base + timedelta(hours=1),
    })

    assert service.list_health_checks() == [second, first]
    assert service.list_health_checks(search="QUEUE") == [second]
    assert service.list_health_checks(checked_from=base + timedelta(minutes=30)) == [second]
    assert service.list_health_checks(created_to=base) == [first]
    assert service.list_health_checks(limit=1, offset=1) == [first]
    assert service.count_health_checks(status=HealthCheckStatus.HEALTHY) == 1
    original_uuid = first.record_uuid
    assert service.update_health_check(first.id, {
        "component": "gateway", "details": {"nested": {"ok": True}},
    }) is first
    assert first.details == {"nested": {"ok": True}}
    assert service.mark_health_check_status(first.id, HealthCheckStatus.DEGRADED) is first
    assert first.status == "degraded" and first.record_uuid == original_uuid
    assert service.health_check_exists(first.id) is True
    assert service.update_health_check(999_999, {"status": "healthy"}) is None

    with pytest.raises(ValueError, match="Unsupported health check record update fields: record_uuid"):
        service.update_health_check(first.id, {"record_uuid": uuid4()})


def test_metric_filters_ordering_pagination_updates_and_json(
    service: MonitoringHealthService,
) -> None:
    base = datetime(2026, 7, 10, 9, 0, tzinfo=timezone.utc)
    first = service.create_metric(MonitoringMetric(
        metric_name="db.connections", category="database", source="db-1",
        value=7, unit="count", labels={"pool": "main"}, details={"raw": [7]},
        recorded_at=base, created_at=base,
    ))
    second = service.create_metric({
        "metric_name": "http.latency", "category": "application", "source": "api",
        "value": 25.5, "unit": "ms", "recorded_at": base + timedelta(hours=1),
        "created_at": base + timedelta(hours=1),
    })

    assert service.list_metrics() == [second, first]
    assert service.list_metrics(search="CONNECTIONS") == [first]
    assert service.list_metrics(unit="ms", recorded_from=base + timedelta(minutes=30)) == [second]
    assert service.list_metrics(created_to=base, limit=1, offset=0) == [first]
    assert service.count_metrics(category=MonitoringMetricCategory.DATABASE) == 1
    original_uuid = first.metric_uuid
    assert service.update_metric(first.id, {
        "value": 8.5, "labels": {"pool": "main", "state": "busy"},
    }) is first
    assert first.value == 8.5 and first.labels == {"pool": "main", "state": "busy"}
    assert first.metric_uuid == original_uuid and service.metric_exists(first.id)
    assert service.update_metric(999_999, {"value": 1}) is None

    with pytest.raises(ValueError, match="Unsupported monitoring metric update fields: metric_uuid"):
        service.update_metric(first.id, {"metric_uuid": uuid4()})


def test_incident_filters_ordering_pagination_and_metadata(
    service: MonitoringHealthService,
) -> None:
    base = datetime(2026, 7, 10, 10, 0, tzinfo=timezone.utc)
    first = service.create_incident(SystemIncident(
        title="Database latency", severity="high", status="investigating",
        source="apm", component="database", description="Slow queries",
        metadata_json={"ticket": "OPS-15", "tags": ["db"]},
        detected_at=base, created_at=base,
    ))
    second = service.create_incident({
        "title": "Worker recovered", "severity": "low", "status": "resolved",
        "source": "scheduler", "component": "worker", "resolution_summary": "Restarted",
        "detected_at": base + timedelta(hours=1), "resolved_at": base + timedelta(hours=2),
        "created_at": base + timedelta(hours=1),
    })

    assert service.list_incidents() == [second, first]
    assert service.list_incidents(search="SLOW") == [first]
    assert service.list_incidents(severity=SystemIncidentSeverity.LOW, source="scheduler") == [second]
    assert service.list_incidents(resolved_from=base + timedelta(hours=2)) == [second]
    assert service.list_incidents(detected_to=base, created_to=base) == [first]
    assert service.list_incidents(limit=1, offset=1) == [first]
    assert service.count_incidents(status=SystemIncidentStatus.INVESTIGATING) == 1
    original_uuid = first.incident_uuid
    assert service.update_incident(first.id, {"metadata_json": {"ticket": "OPS-16"}}) is first
    assert first.metadata_json == {"ticket": "OPS-16"} and first.incident_uuid == original_uuid
    assert service.incident_exists(first.id)

    with pytest.raises(ValueError, match="Unsupported system incident update fields: incident_uuid"):
        service.update_incident(first.id, {"incident_uuid": uuid4()})


@pytest.mark.parametrize(
    ("operation", "message"),
    [
        (lambda service: service.create_health_check({"component": "  "}), "component must not be empty"),
        (lambda service: service.create_metric({"metric_name": "\t", "value": 1}), "metric_name must not be empty"),
        (lambda service: service.create_incident({"title": " "}), "title must not be empty"),
    ],
)
def test_required_text_validation(
    service: MonitoringHealthService, operation: object, message: str,
) -> None:
    with pytest.raises(ValueError, match=message):
        operation(service)  # type: ignore[operator]


@pytest.mark.parametrize("value", ["1", True, float("nan"), float("inf"), float("-inf")])
def test_metric_value_must_be_a_finite_number(
    service: MonitoringHealthService, value: object,
) -> None:
    with pytest.raises(ValueError, match="value must be a finite number"):
        service.create_metric({"metric_name": "cpu", "value": value})


@pytest.mark.parametrize("value", [-0.1, float("nan"), float("inf"), "12"])
def test_response_time_must_be_finite_and_non_negative(
    service: MonitoringHealthService, value: object,
) -> None:
    with pytest.raises(ValueError, match="response_time_ms must"):
        service.create_health_check({"component": "api", "response_time_ms": value})


def test_update_validation_matches_create_validation(service: MonitoringHealthService) -> None:
    check = service.create_health_check({"component": "api"})
    metric = service.create_metric({"metric_name": "cpu", "value": 1})
    incident = service.create_incident({"title": "Outage"})

    with pytest.raises(ValueError, match="component must not be empty"):
        service.update_health_check(check.id, {"component": " "})
    with pytest.raises(ValueError, match="metric_name must not be empty"):
        service.update_metric(metric.id, {"metric_name": " "})
    with pytest.raises(ValueError, match="title must not be empty"):
        service.update_incident(incident.id, {"title": " "})
    with pytest.raises(ValueError, match="Invalid incident status"):
        service.update_incident(incident.id, {"status": "cancelled"})


@pytest.mark.parametrize(
    "call",
    [
        lambda service, later, earlier: service.count_metrics(recorded_from=later, recorded_to=earlier),
        lambda service, later, earlier: service.list_metrics(created_from=later, created_to=earlier),
        lambda service, later, earlier: service.count_incidents(detected_from=later, detected_to=earlier),
        lambda service, later, earlier: service.list_incidents(resolved_from=later, resolved_to=earlier),
        lambda service, later, earlier: service.count_incidents(created_from=later, created_to=earlier),
    ],
)
def test_filter_range_validation(service: MonitoringHealthService, call: object) -> None:
    earlier = datetime(2026, 7, 10, tzinfo=timezone.utc)
    later = earlier + timedelta(seconds=1)
    with pytest.raises(ValueError, match="_from must be earlier than or equal to"):
        call(service, later, earlier)  # type: ignore[operator]


def test_latest_lookup_and_pagination_validation(service: MonitoringHealthService) -> None:
    with pytest.raises(ValueError, match="component must not be empty"):
        service.get_latest_health_check(" ")
    with pytest.raises(ValueError, match="metric_name must not be empty"):
        service.get_latest_metric(" ")
    with pytest.raises(ValueError, match="limit must be greater than zero"):
        service.list_incidents(limit=-1)
    with pytest.raises(ValueError, match="offset must be greater than or equal to zero"):
        service.list_health_checks(offset=-1)
    with pytest.raises(ValueError, match="Invalid incident severity"):
        service.count_incidents(severity="urgent")
    with pytest.raises(ValueError, match="Invalid metric category"):
        service.list_metrics(category="network")


def test_incident_resolution_timestamp_and_missing_lifecycle_behavior(
    service: MonitoringHealthService,
) -> None:
    detected_at = datetime(2026, 7, 10, 12, 0, tzinfo=timezone.utc)
    incident = service.create_incident({"title": "Outage", "detected_at": detected_at})

    with pytest.raises(ValueError, match="resolved_at must be later"):
        service.mark_incident_status(
            incident.id, "resolved", resolved_at=detected_at - timedelta(seconds=1),
        )
    with pytest.raises(ValueError, match="resolved_at must be later"):
        service.update_incident(incident.id, {
            "status": "closed", "resolved_at": detected_at - timedelta(seconds=1),
        })
    with pytest.raises(ValueError, match="resolved_at is only valid"):
        service.mark_incident_status(incident.id, "mitigated", resolved_at=detected_at)

    assert service.mark_incident_status(999_999, "resolved") is None
    assert service.mark_incident_status(incident.id, "investigating") is incident
    assert incident.status == "investigating" and incident.resolved_at is None


def test_compatibility_aliases_preserve_public_behavior(
    service: MonitoringHealthService,
) -> None:
    check = service.create_health_check_record({"component": "api"})
    metric = service.create_monitoring_metric({"metric_name": "cpu", "value": 1})
    incident = service.create_system_incident({"title": "Outage"})

    assert service.get_by_id(check.id) is check
    assert service.get_health_check_record_by_uuid(check.record_uuid) is check
    assert service.list_health_check_records() == [check]
    assert service.count_health_check_records() == 1
    assert service.get_monitoring_metric_by_id(metric.id) is metric
    assert service.monitoring_metric_exists(metric.id)
    assert service.get_system_incident_by_id(incident.id) is incident
    assert service.system_incident_exists(incident.id)


@pytest.mark.parametrize(
    ("create", "field"),
    [
        (lambda service: service.create_health_check({"component": 42}), "component"),
        (lambda service: service.create_metric({"metric_name": ["cpu"], "value": 1}), "metric_name"),
        (lambda service: service.create_incident({"title": {"name": "Outage"}}), "title"),
    ],
)
def test_create_rejects_non_string_required_fields(
    service: MonitoringHealthService, create: object, field: str,
) -> None:
    with pytest.raises(ValueError, match=rf"{field} must be a string"):
        create(service)  # type: ignore[operator]


def test_updates_reject_non_string_required_fields(
    service: MonitoringHealthService,
) -> None:
    check = service.create_health_check({"component": "api"})
    metric = service.create_metric({"metric_name": "cpu", "value": 1})
    incident = service.create_incident({"title": "Outage"})

    with pytest.raises(ValueError, match="component must be a string"):
        service.update_health_check(check.id, {"component": 1})
    with pytest.raises(ValueError, match="metric_name must be a string"):
        service.update_metric(metric.id, {"metric_name": False})
    with pytest.raises(ValueError, match="title must be a string"):
        service.update_incident(incident.id, {"title": ["Outage"]})


def test_resolution_summary_is_strictly_validated_without_coercion(
    service: MonitoringHealthService,
) -> None:
    with pytest.raises(ValueError, match="resolution_summary must be a string"):
        service.create_incident({
            "title": "Outage", "status": "resolved", "resolution_summary": 123,
        })

    incident = service.create_incident({"title": "Outage"})
    with pytest.raises(ValueError, match="resolution_summary must be a string"):
        service.update_incident(incident.id, {"resolution_summary": {"text": "fixed"}})
    with pytest.raises(ValueError, match="resolution_summary must be a string"):
        service.mark_incident_status(
            incident.id, "resolved", resolution_summary=123  # type: ignore[arg-type]
        )


def test_mixed_datetime_ranges_use_persisted_utc_assumption(
    service: MonitoringHealthService,
) -> None:
    aware_earlier = datetime(2026, 7, 10, 8, 0, tzinfo=timezone.utc)
    naive_later = datetime(2026, 7, 10, 9, 0)

    with pytest.raises(ValueError, match="checked_from must be earlier"):
        service.list_health_checks(
            checked_from=naive_later, checked_to=aware_earlier,
        )
    with pytest.raises(ValueError, match="recorded_from must be earlier"):
        service.count_metrics(
            recorded_from=naive_later, recorded_to=aware_earlier,
        )
    with pytest.raises(ValueError, match="detected_from must be earlier"):
        service.list_incidents(
            detected_from=naive_later, detected_to=aware_earlier,
        )


def test_naive_lifecycle_timestamps_are_compared_as_utc(
    service: MonitoringHealthService,
) -> None:
    detected_at = datetime(2026, 7, 10, 10, 0)
    incident = service.create_incident({"title": "Outage", "detected_at": detected_at})

    resolved = service.mark_incident_status(
        incident.id,
        "resolved",
        resolved_at=datetime(2026, 7, 10, 11, 0, tzinfo=timezone.utc),
    )
    assert resolved is incident

    service.mark_incident_status(incident.id, "open")
    with pytest.raises(ValueError, match="resolved_at must be later"):
        service.mark_incident_status(
            incident.id, "resolved", resolved_at=datetime(2026, 7, 10, 9, 0),
        )


def test_generic_and_dedicated_terminal_updates_share_lifecycle_rules(
    service: MonitoringHealthService,
) -> None:
    generic = service.create_incident({"title": "Generic"})
    dedicated = service.create_incident({"title": "Dedicated"})

    assert service.update_incident(generic.id, {
        "status": "resolved", "resolution_summary": "Recovered",
    }) is generic
    assert service.mark_incident_status(
        dedicated.id, "resolved", resolution_summary="Recovered",
    ) is dedicated
    assert generic.resolved_at is not None
    assert dedicated.resolved_at is not None

    assert service.update_incident(generic.id, {"status": "investigating"}) is generic
    assert service.mark_incident_status(dedicated.id, "investigating") is dedicated
    assert generic.resolved_at is None and dedicated.resolved_at is None
    assert generic.resolution_summary == "Recovered"
    assert dedicated.resolution_summary == "Recovered"


def test_missing_incident_precedes_lifecycle_value_validation(
    service: MonitoringHealthService,
) -> None:
    assert service.mark_incident_status(999_999, "not-a-status") is None
