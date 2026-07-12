"""Service layer for the Monitoring & Health module."""

from __future__ import annotations

from collections.abc import Mapping
from datetime import datetime, timezone
from math import isfinite
from typing import Any, TypeVar
from uuid import UUID

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
from app.modules.monitoring_health.schemas import MonitoringHealthHealthRead

Payload = Mapping[str, Any]
EnumType = TypeVar("EnumType", HealthCheckStatus, MonitoringMetricCategory, SystemIncidentSeverity, SystemIncidentStatus)


class MonitoringHealthService:
    """Business boundary for health checks and operational diagnostics."""

    def __init__(self, repository: MonitoringHealthRepository) -> None:
        self.repository = repository
        self.health_checks = repository.health_checks
        self.metrics = repository.metrics
        self.incidents = repository.incidents

    def health(self) -> MonitoringHealthHealthRead:
        """Return aggregate Monitoring & Health module health."""

        return MonitoringHealthHealthRead(
            module="monitoring_health",
            status="ok" if self.repository.health() else "error",
        )

    def get_module_status(self) -> dict[str, object]:
        """Return aggregate module and repository health."""

        checks = {
            "health_checks": self._safe_health(self.health_checks),
            "metrics": self._safe_health(self.metrics),
            "incidents": self._safe_health(self.incidents),
        }
        return {
            "module": "monitoring_health",
            "status": "ok" if all(checks.values()) else "error",
            "repositories": checks,
        }

    # Health check records

    def create_health_check(self, payload: Payload | HealthCheckRecord) -> HealthCheckRecord:
        record = payload if isinstance(payload, HealthCheckRecord) else HealthCheckRecord(**dict(payload))
        self._require_text(record.component, "component")
        self._validate_enum(record.status, HealthCheckStatus, "health check status")
        self._validate_non_negative_number(record.response_time_ms, "response_time_ms")
        return self.health_checks.create_record(record)

    def get_health_check(self, record_id: int) -> HealthCheckRecord | None:
        return self.health_checks.get_by_id(record_id)

    def get_health_check_by_id(self, record_id: int) -> HealthCheckRecord | None:
        return self.get_health_check(record_id)

    def get_health_check_by_uuid(self, record_uuid: UUID) -> HealthCheckRecord | None:
        return self.health_checks.get_by_uuid(record_uuid)

    def get_latest_health_check(self, component: str) -> HealthCheckRecord | None:
        self._require_text(component, "component")
        return self.health_checks.get_latest_for_component(component)

    def list_health_checks(
        self, *, component: str | None = None,
        status: str | HealthCheckStatus | None = None,
        checked_from: datetime | None = None, checked_to: datetime | None = None,
        created_from: datetime | None = None, created_to: datetime | None = None,
        search: str | None = None, limit: int | None = None, offset: int | None = None,
    ) -> list[HealthCheckRecord]:
        self._validate_enum(status, HealthCheckStatus, "health check status")
        self._validate_range(checked_from, checked_to, "checked")
        self._validate_range(created_from, created_to, "created")
        self._validate_pagination(limit, offset)
        return self.health_checks.list(component=component, status=status, checked_from=checked_from,
            checked_to=checked_to, created_from=created_from, created_to=created_to,
            search=search, limit=limit, offset=offset)

    def count_health_checks(
        self, *, component: str | None = None,
        status: str | HealthCheckStatus | None = None,
        checked_from: datetime | None = None, checked_to: datetime | None = None,
        created_from: datetime | None = None, created_to: datetime | None = None,
        search: str | None = None,
    ) -> int:
        self._validate_enum(status, HealthCheckStatus, "health check status")
        self._validate_range(checked_from, checked_to, "checked")
        self._validate_range(created_from, created_to, "created")
        return self.health_checks.count(component=component, status=status, checked_from=checked_from,
            checked_to=checked_to, created_from=created_from, created_to=created_to, search=search)

    def update_health_check(self, record_id: int, values: Payload) -> HealthCheckRecord | None:
        if "component" in values:
            self._require_text(values["component"], "component")
        if "status" in values:
            self._validate_enum(values["status"], HealthCheckStatus, "health check status")
        if "response_time_ms" in values:
            self._validate_non_negative_number(values["response_time_ms"], "response_time_ms")
        return self.health_checks.update(record_id, values)

    def mark_health_check_status(self, record_id: int, status: str | HealthCheckStatus) -> HealthCheckRecord | None:
        self._validate_enum(status, HealthCheckStatus, "health check status")
        return self.health_checks.update(record_id, {"status": self._enum_value(status)})

    def health_check_exists(self, record_id: int) -> bool:
        return self.health_checks.exists(record_id)

    # Monitoring metric samples

    def create_metric(self, payload: Payload | MonitoringMetric) -> MonitoringMetric:
        metric = payload if isinstance(payload, MonitoringMetric) else MonitoringMetric(**dict(payload))
        self._require_text(metric.metric_name, "metric_name")
        self._validate_enum(metric.category, MonitoringMetricCategory, "metric category")
        self._validate_number(metric.value, "value")
        return self.metrics.create_metric(metric)

    def get_metric(self, metric_id: int) -> MonitoringMetric | None:
        return self.metrics.get_by_id(metric_id)

    def get_metric_by_id(self, metric_id: int) -> MonitoringMetric | None:
        return self.get_metric(metric_id)

    def get_metric_by_uuid(self, metric_uuid: UUID) -> MonitoringMetric | None:
        return self.metrics.get_by_uuid(metric_uuid)

    def get_latest_metric(self, metric_name: str, *, source: str | None = None) -> MonitoringMetric | None:
        self._require_text(metric_name, "metric_name")
        return self.metrics.get_latest_by_name(metric_name, source=source)

    def list_metrics(
        self, *, metric_name: str | None = None,
        category: str | MonitoringMetricCategory | None = None,
        source: str | None = None, unit: str | None = None,
        recorded_from: datetime | None = None, recorded_to: datetime | None = None,
        created_from: datetime | None = None, created_to: datetime | None = None,
        search: str | None = None, limit: int | None = None, offset: int | None = None,
    ) -> list[MonitoringMetric]:
        self._validate_enum(category, MonitoringMetricCategory, "metric category")
        self._validate_range(recorded_from, recorded_to, "recorded")
        self._validate_range(created_from, created_to, "created")
        self._validate_pagination(limit, offset)
        return self.metrics.list(metric_name=metric_name, category=category, source=source, unit=unit,
            recorded_from=recorded_from, recorded_to=recorded_to, created_from=created_from,
            created_to=created_to, search=search, limit=limit, offset=offset)

    def count_metrics(
        self, *, metric_name: str | None = None,
        category: str | MonitoringMetricCategory | None = None,
        source: str | None = None, unit: str | None = None,
        recorded_from: datetime | None = None, recorded_to: datetime | None = None,
        created_from: datetime | None = None, created_to: datetime | None = None,
        search: str | None = None,
    ) -> int:
        self._validate_enum(category, MonitoringMetricCategory, "metric category")
        self._validate_range(recorded_from, recorded_to, "recorded")
        self._validate_range(created_from, created_to, "created")
        return self.metrics.count(metric_name=metric_name, category=category, source=source, unit=unit,
            recorded_from=recorded_from, recorded_to=recorded_to, created_from=created_from,
            created_to=created_to, search=search)

    def update_metric(self, metric_id: int, values: Payload) -> MonitoringMetric | None:
        if "metric_name" in values:
            self._require_text(values["metric_name"], "metric_name")
        if "category" in values:
            self._validate_enum(values["category"], MonitoringMetricCategory, "metric category")
        if "value" in values:
            self._validate_number(values["value"], "value")
        return self.metrics.update(metric_id, values)

    def metric_exists(self, metric_id: int) -> bool:
        return self.metrics.exists(metric_id)

    # System incidents

    def create_incident(self, payload: Payload | SystemIncident) -> SystemIncident:
        incident = payload if isinstance(payload, SystemIncident) else SystemIncident(**dict(payload))
        self._require_text(incident.title, "title")
        self._validate_enum(incident.severity, SystemIncidentSeverity, "incident severity")
        self._validate_enum(incident.status, SystemIncidentStatus, "incident status")
        self._validate_incident_resolution(
            incident.status,
            resolved_at=incident.resolved_at,
            resolution_summary=incident.resolution_summary,
        )
        self._validate_resolution_timestamp(incident.detected_at, incident.resolved_at)
        return self.incidents.create_incident(incident)

    def get_incident(self, incident_id: int) -> SystemIncident | None:
        return self.incidents.get_by_id(incident_id)

    def get_incident_by_id(self, incident_id: int) -> SystemIncident | None:
        return self.get_incident(incident_id)

    def get_incident_by_uuid(self, incident_uuid: UUID) -> SystemIncident | None:
        return self.incidents.get_by_uuid(incident_uuid)

    def list_incidents(
        self, *, title: str | None = None,
        severity: str | SystemIncidentSeverity | None = None,
        status: str | SystemIncidentStatus | None = None, source: str | None = None,
        component: str | None = None, detected_from: datetime | None = None,
        detected_to: datetime | None = None, resolved_from: datetime | None = None,
        resolved_to: datetime | None = None, created_from: datetime | None = None,
        created_to: datetime | None = None, search: str | None = None,
        limit: int | None = None, offset: int | None = None,
    ) -> list[SystemIncident]:
        self._validate_incident_filters(severity, status, detected_from, detected_to,
            resolved_from, resolved_to, created_from, created_to)
        self._validate_pagination(limit, offset)
        return self.incidents.list(title=title, severity=severity, status=status, source=source,
            component=component, detected_from=detected_from, detected_to=detected_to,
            resolved_from=resolved_from, resolved_to=resolved_to, created_from=created_from,
            created_to=created_to, search=search, limit=limit, offset=offset)

    def count_incidents(
        self, *, title: str | None = None,
        severity: str | SystemIncidentSeverity | None = None,
        status: str | SystemIncidentStatus | None = None, source: str | None = None,
        component: str | None = None, detected_from: datetime | None = None,
        detected_to: datetime | None = None, resolved_from: datetime | None = None,
        resolved_to: datetime | None = None, created_from: datetime | None = None,
        created_to: datetime | None = None, search: str | None = None,
    ) -> int:
        self._validate_incident_filters(severity, status, detected_from, detected_to,
            resolved_from, resolved_to, created_from, created_to)
        return self.incidents.count(title=title, severity=severity, status=status, source=source,
            component=component, detected_from=detected_from, detected_to=detected_to,
            resolved_from=resolved_from, resolved_to=resolved_to, created_from=created_from,
            created_to=created_to, search=search)

    def update_incident(self, incident_id: int, values: Payload) -> SystemIncident | None:
        incident = self.incidents.get_by_id(incident_id)
        if incident is None:
            return None
        if "title" in values:
            self._require_text(values["title"], "title")
        if "severity" in values:
            self._validate_enum(values["severity"], SystemIncidentSeverity, "incident severity")
        if "status" in values:
            self._validate_enum(values["status"], SystemIncidentStatus, "incident status")
        update_values = self._prepare_incident_lifecycle_update(incident, values)
        return self.incidents.update(incident_id, update_values)

    def mark_incident_status(
        self, incident_id: int, status: str | SystemIncidentStatus, *,
        resolution_summary: str | None = None, resolved_at: datetime | None = None,
    ) -> SystemIncident | None:
        incident = self.incidents.get_by_id(incident_id)
        if incident is None:
            return None
        self._validate_enum(status, SystemIncidentStatus, "incident status")
        status_value = self._enum_value(status)
        values: dict[str, object] = {"status": status_value}
        if resolution_summary is not None:
            self._require_text(resolution_summary, "resolution_summary")
            values["resolution_summary"] = resolution_summary
        if resolved_at is not None:
            values["resolved_at"] = resolved_at
        update_values = self._prepare_incident_lifecycle_update(incident, values)
        return self.incidents.update(incident_id, update_values)

    def incident_exists(self, incident_id: int) -> bool:
        return self.incidents.exists(incident_id)

    # Compatibility aliases
    create = create_health_check
    get_by_id = get_health_check_by_id
    get_by_uuid = get_health_check_by_uuid
    list = list_health_checks
    count = count_health_checks
    update = update_health_check
    exists = health_check_exists

    create_health_check_record = create_health_check
    get_health_check_record = get_health_check
    get_health_check_record_by_id = get_health_check_by_id
    get_health_check_record_by_uuid = get_health_check_by_uuid
    list_health_check_records = list_health_checks
    count_health_check_records = count_health_checks
    update_health_check_record = update_health_check
    health_check_record_exists = health_check_exists

    create_monitoring_metric = create_metric
    get_monitoring_metric = get_metric
    get_monitoring_metric_by_id = get_metric_by_id
    get_monitoring_metric_by_uuid = get_metric_by_uuid
    list_monitoring_metrics = list_metrics
    count_monitoring_metrics = count_metrics
    update_monitoring_metric = update_metric
    monitoring_metric_exists = metric_exists

    create_system_incident = create_incident
    get_system_incident = get_incident
    get_system_incident_by_id = get_incident_by_id
    get_system_incident_by_uuid = get_incident_by_uuid
    list_system_incidents = list_incidents
    count_system_incidents = count_incidents
    update_system_incident = update_incident
    mark_system_incident_status = mark_incident_status
    system_incident_exists = incident_exists

    @staticmethod
    def _validate_enum(value: object | None, enum_type: type[EnumType], label: str) -> None:
        if value is None:
            return
        candidate = value.value if isinstance(value, enum_type) else value
        try:
            enum_type(candidate)
        except (TypeError, ValueError) as exc:
            allowed = ", ".join(item.value for item in enum_type)
            raise ValueError(f"Invalid {label}: {candidate!r}. Expected one of: {allowed}.") from exc

    @staticmethod
    def _enum_value(value: str | SystemIncidentStatus | HealthCheckStatus) -> str:
        return value.value if isinstance(value, (SystemIncidentStatus, HealthCheckStatus)) else value

    @staticmethod
    def _require_text(value: object, field: str) -> None:
        if not isinstance(value, str):
            raise ValueError(f"{field} must be a string.")
        if not value.strip():
            raise ValueError(f"{field} must not be empty.")

    @staticmethod
    def _validate_number(value: object, field: str) -> None:
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise ValueError(f"{field} must be a finite number.")
        if not isfinite(value):
            raise ValueError(f"{field} must be a finite number.")

    @classmethod
    def _validate_non_negative_number(cls, value: object | None, field: str) -> None:
        if value is None:
            return
        cls._validate_number(value, field)
        if float(value) < 0:
            raise ValueError(f"{field} must be greater than or equal to zero.")

    @classmethod
    def _validate_resolution_timestamp(
        cls,
        detected_at: object | None, resolved_at: object | None
    ) -> None:
        if isinstance(detected_at, datetime) and isinstance(resolved_at, datetime):
            comparable_detected_at = cls._as_utc(detected_at)
            comparable_resolved_at = cls._as_utc(resolved_at)
        else:
            return
        if comparable_resolved_at < comparable_detected_at:
            raise ValueError("resolved_at must be later than or equal to detected_at.")

    @classmethod
    def _validate_range(cls, start: datetime | None, end: datetime | None, label: str) -> None:
        if start is not None and end is not None and cls._as_utc(start) > cls._as_utc(end):
            raise ValueError(f"{label}_from must be earlier than or equal to {label}_to.")

    @staticmethod
    def _as_utc(value: datetime) -> datetime:
        """Normalize timestamps for comparison; persisted naive values represent UTC."""

        if value.tzinfo is None:
            return value.replace(tzinfo=timezone.utc)
        return value.astimezone(timezone.utc)

    @staticmethod
    def _validate_pagination(limit: int | None, offset: int | None) -> None:
        if limit is not None and limit <= 0:
            raise ValueError("limit must be greater than zero.")
        if offset is not None and offset < 0:
            raise ValueError("offset must be greater than or equal to zero.")

    @staticmethod
    def _validate_incident_resolution(
        status: object,
        *,
        resolved_at: object | None,
        resolution_summary: object | None,
    ) -> None:
        status_value = (
            status.value if isinstance(status, SystemIncidentStatus) else status
        )
        terminal = {
            SystemIncidentStatus.RESOLVED.value,
            SystemIncidentStatus.CLOSED.value,
        }
        if status_value not in terminal and resolved_at is not None:
            raise ValueError(
                "resolved_at is only valid for resolved or closed incidents."
            )
        if resolution_summary is not None:
            MonitoringHealthService._require_text(
                resolution_summary, "resolution_summary"
            )

    @classmethod
    def _prepare_incident_lifecycle_update(
        cls, incident: SystemIncident, values: Payload
    ) -> dict[str, object]:
        update_values = dict(values)
        current_status = cls._enum_value(incident.status)
        effective_status = cls._enum_value(values.get("status", incident.status))
        terminal_statuses = {
            SystemIncidentStatus.RESOLVED.value,
            SystemIncidentStatus.CLOSED.value,
        }
        is_terminal = effective_status in terminal_statuses
        was_terminal = current_status in terminal_statuses

        if is_terminal and not was_terminal and update_values.get("resolved_at") is None:
            update_values["resolved_at"] = datetime.now(timezone.utc)
        elif not is_terminal:
            if update_values.get("resolved_at") is not None and not was_terminal:
                raise ValueError(
                    "resolved_at is only valid for resolved or closed incidents."
                )
            update_values["resolved_at"] = None

        effective_resolved_at = update_values.get("resolved_at", incident.resolved_at)
        effective_summary = update_values.get(
            "resolution_summary", incident.resolution_summary
        )
        cls._validate_incident_resolution(
            effective_status,
            resolved_at=effective_resolved_at,
            resolution_summary=effective_summary,
        )
        cls._validate_resolution_timestamp(
            update_values.get("detected_at", incident.detected_at),
            effective_resolved_at,
        )
        return update_values

    @classmethod
    def _validate_incident_filters(cls, severity: object | None, status: object | None,
        detected_from: datetime | None, detected_to: datetime | None,
        resolved_from: datetime | None, resolved_to: datetime | None,
        created_from: datetime | None, created_to: datetime | None) -> None:
        cls._validate_enum(severity, SystemIncidentSeverity, "incident severity")
        cls._validate_enum(status, SystemIncidentStatus, "incident status")
        cls._validate_range(detected_from, detected_to, "detected")
        cls._validate_range(resolved_from, resolved_to, "resolved")
        cls._validate_range(created_from, created_to, "created")

    @staticmethod
    def _safe_health(repository: object) -> bool:
        try:
            return bool(repository.health())  # type: ignore[attr-defined]
        except Exception:
            return False


__all__ = ["MonitoringHealthService"]
