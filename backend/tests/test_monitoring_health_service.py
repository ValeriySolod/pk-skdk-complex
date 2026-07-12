from __future__ import annotations

from datetime import datetime, timedelta, timezone
from uuid import uuid4

import pytest
from sqlalchemy.orm import Session

from app.modules.monitoring_health.models import SystemIncidentStatus
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
