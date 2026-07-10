"""Repository operations for the Monitoring & Health module."""

from __future__ import annotations

from collections.abc import Mapping
from datetime import datetime
from enum import Enum
from uuid import UUID

from sqlalchemy import Select, func, or_, select
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


def _enum_value(value: str | Enum | None) -> str | None:
    if value is None:
        return None
    if isinstance(value, Enum):
        return str(value.value)
    return value


class HealthCheckRecordRepository:
    """Persistence operations for component health check records."""

    _mutable_fields = frozenset(
        {
            "component",
            "status",
            "response_time_ms",
            "message",
            "details",
            "checked_at",
        },
    )

    def __init__(self, db: Session) -> None:
        self.db = db

    def create(self, record: HealthCheckRecord) -> HealthCheckRecord:
        """Create a health check record."""

        self.db.add(record)
        self.db.flush()
        return record

    def create_record(self, record: HealthCheckRecord) -> HealthCheckRecord:
        """Create a health check record using the module alias."""

        return self.create(record)

    def get_by_id(self, record_id: int) -> HealthCheckRecord | None:
        """Get a health check record by integer ID."""

        return self.db.get(HealthCheckRecord, record_id)

    def get_by_uuid(self, record_uuid: UUID) -> HealthCheckRecord | None:
        """Get a health check record by UUID."""

        return self.db.scalar(
            select(HealthCheckRecord).where(
                HealthCheckRecord.record_uuid == record_uuid,
            ),
        )

    def get_latest_for_component(
        self,
        component: str,
    ) -> HealthCheckRecord | None:
        """Get the latest health check record for a component."""

        return self.db.scalar(
            select(HealthCheckRecord)
            .where(HealthCheckRecord.component == component)
            .order_by(
                HealthCheckRecord.checked_at.desc(),
                HealthCheckRecord.id.desc(),
            ),
        )

    def list(
        self,
        *,
        component: str | None = None,
        status: str | HealthCheckStatus | None = None,
        checked_from: datetime | None = None,
        checked_to: datetime | None = None,
        created_from: datetime | None = None,
        created_to: datetime | None = None,
        search: str | None = None,
        limit: int | None = None,
        offset: int | None = None,
    ) -> list[HealthCheckRecord]:
        """List health check records using repository filters."""

        query = self._build_query(
            component=component,
            status=status,
            checked_from=checked_from,
            checked_to=checked_to,
            created_from=created_from,
            created_to=created_to,
            search=search,
        ).order_by(HealthCheckRecord.created_at.desc(), HealthCheckRecord.id.desc())

        if offset is not None:
            query = query.offset(offset)
        if limit is not None:
            query = query.limit(limit)

        return list(self.db.scalars(query).all())

    def count(
        self,
        *,
        component: str | None = None,
        status: str | HealthCheckStatus | None = None,
        checked_from: datetime | None = None,
        checked_to: datetime | None = None,
        created_from: datetime | None = None,
        created_to: datetime | None = None,
        search: str | None = None,
    ) -> int:
        """Count health check records using repository filters."""

        query = self._build_query(
            component=component,
            status=status,
            checked_from=checked_from,
            checked_to=checked_to,
            created_from=created_from,
            created_to=created_to,
            search=search,
        )
        return self.db.scalar(select(func.count()).select_from(query.subquery())) or 0

    def update(
        self,
        record_id: int,
        values: Mapping[str, object],
    ) -> HealthCheckRecord | None:
        """Update mutable health check record fields."""

        record = self.get_by_id(record_id)
        if record is None:
            return None

        unsupported_fields = set(values) - self._mutable_fields
        if unsupported_fields:
            fields = ", ".join(sorted(unsupported_fields))
            raise ValueError(f"Unsupported health check record update fields: {fields}")

        for field, value in values.items():
            setattr(record, field, value)

        self.db.flush()
        return record

    def exists(self, record_id: int) -> bool:
        """Return whether a health check record exists."""

        return self.get_by_id(record_id) is not None

    def health(self) -> bool:
        """Return whether the health check repository can reach the database."""

        return self.db.scalar(select(1)) == 1

    def _build_query(
        self,
        *,
        component: str | None = None,
        status: str | HealthCheckStatus | None = None,
        checked_from: datetime | None = None,
        checked_to: datetime | None = None,
        created_from: datetime | None = None,
        created_to: datetime | None = None,
        search: str | None = None,
    ) -> Select[tuple[HealthCheckRecord]]:
        query = select(HealthCheckRecord)
        status_value = _enum_value(status)

        if component is not None:
            query = query.where(HealthCheckRecord.component == component)
        if status_value is not None:
            query = query.where(HealthCheckRecord.status == status_value)
        if checked_from is not None:
            query = query.where(HealthCheckRecord.checked_at >= checked_from)
        if checked_to is not None:
            query = query.where(HealthCheckRecord.checked_at <= checked_to)
        if created_from is not None:
            query = query.where(HealthCheckRecord.created_at >= created_from)
        if created_to is not None:
            query = query.where(HealthCheckRecord.created_at <= created_to)
        if search is not None:
            term = f"%{search}%"
            query = query.where(
                or_(
                    HealthCheckRecord.component.ilike(term),
                    HealthCheckRecord.message.ilike(term),
                ),
            )

        return query


class MonitoringMetricRepository:
    """Persistence operations for monitoring metric samples."""

    _mutable_fields = frozenset(
        {
            "metric_name",
            "category",
            "source",
            "value",
            "unit",
            "labels",
            "details",
            "recorded_at",
        },
    )

    def __init__(self, db: Session) -> None:
        self.db = db

    def create(self, metric: MonitoringMetric) -> MonitoringMetric:
        """Create a monitoring metric sample."""

        self.db.add(metric)
        self.db.flush()
        return metric

    def create_metric(self, metric: MonitoringMetric) -> MonitoringMetric:
        """Create a monitoring metric sample using the module alias."""

        return self.create(metric)

    def get_by_id(self, metric_id: int) -> MonitoringMetric | None:
        """Get a monitoring metric sample by integer ID."""

        return self.db.get(MonitoringMetric, metric_id)

    def get_by_uuid(self, metric_uuid: UUID) -> MonitoringMetric | None:
        """Get a monitoring metric sample by UUID."""

        return self.db.scalar(
            select(MonitoringMetric).where(
                MonitoringMetric.metric_uuid == metric_uuid,
            ),
        )

    def get_latest_by_name(
        self,
        metric_name: str,
        *,
        source: str | None = None,
    ) -> MonitoringMetric | None:
        """Get the latest monitoring metric sample for a metric name."""

        query = select(MonitoringMetric).where(
            MonitoringMetric.metric_name == metric_name,
        )
        if source is not None:
            query = query.where(MonitoringMetric.source == source)
        return self.db.scalar(
            query.order_by(
                MonitoringMetric.recorded_at.desc(),
                MonitoringMetric.id.desc(),
            ),
        )

    def list(
        self,
        *,
        metric_name: str | None = None,
        category: str | MonitoringMetricCategory | None = None,
        source: str | None = None,
        unit: str | None = None,
        recorded_from: datetime | None = None,
        recorded_to: datetime | None = None,
        created_from: datetime | None = None,
        created_to: datetime | None = None,
        search: str | None = None,
        limit: int | None = None,
        offset: int | None = None,
    ) -> list[MonitoringMetric]:
        """List monitoring metric samples using repository filters."""

        query = self._build_query(
            metric_name=metric_name,
            category=category,
            source=source,
            unit=unit,
            recorded_from=recorded_from,
            recorded_to=recorded_to,
            created_from=created_from,
            created_to=created_to,
            search=search,
        ).order_by(MonitoringMetric.created_at.desc(), MonitoringMetric.id.desc())

        if offset is not None:
            query = query.offset(offset)
        if limit is not None:
            query = query.limit(limit)

        return list(self.db.scalars(query).all())

    def count(
        self,
        *,
        metric_name: str | None = None,
        category: str | MonitoringMetricCategory | None = None,
        source: str | None = None,
        unit: str | None = None,
        recorded_from: datetime | None = None,
        recorded_to: datetime | None = None,
        created_from: datetime | None = None,
        created_to: datetime | None = None,
        search: str | None = None,
    ) -> int:
        """Count monitoring metric samples using repository filters."""

        query = self._build_query(
            metric_name=metric_name,
            category=category,
            source=source,
            unit=unit,
            recorded_from=recorded_from,
            recorded_to=recorded_to,
            created_from=created_from,
            created_to=created_to,
            search=search,
        )
        return self.db.scalar(select(func.count()).select_from(query.subquery())) or 0

    def update(
        self,
        metric_id: int,
        values: Mapping[str, object],
    ) -> MonitoringMetric | None:
        """Update mutable monitoring metric sample fields."""

        metric = self.get_by_id(metric_id)
        if metric is None:
            return None

        unsupported_fields = set(values) - self._mutable_fields
        if unsupported_fields:
            fields = ", ".join(sorted(unsupported_fields))
            raise ValueError(f"Unsupported monitoring metric update fields: {fields}")

        for field, value in values.items():
            setattr(metric, field, value)

        self.db.flush()
        return metric

    def exists(self, metric_id: int) -> bool:
        """Return whether a monitoring metric sample exists."""

        return self.get_by_id(metric_id) is not None

    def health(self) -> bool:
        """Return whether the metric repository can reach the database."""

        return self.db.scalar(select(1)) == 1

    def _build_query(
        self,
        *,
        metric_name: str | None = None,
        category: str | MonitoringMetricCategory | None = None,
        source: str | None = None,
        unit: str | None = None,
        recorded_from: datetime | None = None,
        recorded_to: datetime | None = None,
        created_from: datetime | None = None,
        created_to: datetime | None = None,
        search: str | None = None,
    ) -> Select[tuple[MonitoringMetric]]:
        query = select(MonitoringMetric)
        category_value = _enum_value(category)

        if metric_name is not None:
            query = query.where(MonitoringMetric.metric_name == metric_name)
        if category_value is not None:
            query = query.where(MonitoringMetric.category == category_value)
        if source is not None:
            query = query.where(MonitoringMetric.source == source)
        if unit is not None:
            query = query.where(MonitoringMetric.unit == unit)
        if recorded_from is not None:
            query = query.where(MonitoringMetric.recorded_at >= recorded_from)
        if recorded_to is not None:
            query = query.where(MonitoringMetric.recorded_at <= recorded_to)
        if created_from is not None:
            query = query.where(MonitoringMetric.created_at >= created_from)
        if created_to is not None:
            query = query.where(MonitoringMetric.created_at <= created_to)
        if search is not None:
            term = f"%{search}%"
            query = query.where(
                or_(
                    MonitoringMetric.metric_name.ilike(term),
                    MonitoringMetric.source.ilike(term),
                    MonitoringMetric.unit.ilike(term),
                ),
            )

        return query


class SystemIncidentRepository:
    """Persistence operations for operational incidents."""

    _mutable_fields = frozenset(
        {
            "title",
            "severity",
            "status",
            "source",
            "component",
            "description",
            "resolution_summary",
            "metadata_json",
            "detected_at",
            "resolved_at",
        },
    )

    def __init__(self, db: Session) -> None:
        self.db = db

    def create(self, incident: SystemIncident) -> SystemIncident:
        """Create an operational incident."""

        self.db.add(incident)
        self.db.flush()
        return incident

    def create_incident(self, incident: SystemIncident) -> SystemIncident:
        """Create an operational incident using the module alias."""

        return self.create(incident)

    def get_by_id(self, incident_id: int) -> SystemIncident | None:
        """Get an operational incident by integer ID."""

        return self.db.get(SystemIncident, incident_id)

    def get_by_uuid(self, incident_uuid: UUID) -> SystemIncident | None:
        """Get an operational incident by UUID."""

        return self.db.scalar(
            select(SystemIncident).where(
                SystemIncident.incident_uuid == incident_uuid,
            ),
        )

    def list(
        self,
        *,
        title: str | None = None,
        severity: str | SystemIncidentSeverity | None = None,
        status: str | SystemIncidentStatus | None = None,
        source: str | None = None,
        component: str | None = None,
        detected_from: datetime | None = None,
        detected_to: datetime | None = None,
        resolved_from: datetime | None = None,
        resolved_to: datetime | None = None,
        created_from: datetime | None = None,
        created_to: datetime | None = None,
        search: str | None = None,
        limit: int | None = None,
        offset: int | None = None,
    ) -> list[SystemIncident]:
        """List operational incidents using repository filters."""

        query = self._build_query(
            title=title,
            severity=severity,
            status=status,
            source=source,
            component=component,
            detected_from=detected_from,
            detected_to=detected_to,
            resolved_from=resolved_from,
            resolved_to=resolved_to,
            created_from=created_from,
            created_to=created_to,
            search=search,
        ).order_by(SystemIncident.created_at.desc(), SystemIncident.id.desc())

        if offset is not None:
            query = query.offset(offset)
        if limit is not None:
            query = query.limit(limit)

        return list(self.db.scalars(query).all())

    def count(
        self,
        *,
        title: str | None = None,
        severity: str | SystemIncidentSeverity | None = None,
        status: str | SystemIncidentStatus | None = None,
        source: str | None = None,
        component: str | None = None,
        detected_from: datetime | None = None,
        detected_to: datetime | None = None,
        resolved_from: datetime | None = None,
        resolved_to: datetime | None = None,
        created_from: datetime | None = None,
        created_to: datetime | None = None,
        search: str | None = None,
    ) -> int:
        """Count operational incidents using repository filters."""

        query = self._build_query(
            title=title,
            severity=severity,
            status=status,
            source=source,
            component=component,
            detected_from=detected_from,
            detected_to=detected_to,
            resolved_from=resolved_from,
            resolved_to=resolved_to,
            created_from=created_from,
            created_to=created_to,
            search=search,
        )
        return self.db.scalar(select(func.count()).select_from(query.subquery())) or 0

    def update(
        self,
        incident_id: int,
        values: Mapping[str, object],
    ) -> SystemIncident | None:
        """Update mutable operational incident fields."""

        incident = self.get_by_id(incident_id)
        if incident is None:
            return None

        unsupported_fields = set(values) - self._mutable_fields
        if unsupported_fields:
            fields = ", ".join(sorted(unsupported_fields))
            raise ValueError(f"Unsupported system incident update fields: {fields}")

        for field, value in values.items():
            setattr(incident, field, value)

        self.db.flush()
        return incident

    def exists(self, incident_id: int) -> bool:
        """Return whether an operational incident exists."""

        return self.get_by_id(incident_id) is not None

    def health(self) -> bool:
        """Return whether the incident repository can reach the database."""

        return self.db.scalar(select(1)) == 1

    def _build_query(
        self,
        *,
        title: str | None = None,
        severity: str | SystemIncidentSeverity | None = None,
        status: str | SystemIncidentStatus | None = None,
        source: str | None = None,
        component: str | None = None,
        detected_from: datetime | None = None,
        detected_to: datetime | None = None,
        resolved_from: datetime | None = None,
        resolved_to: datetime | None = None,
        created_from: datetime | None = None,
        created_to: datetime | None = None,
        search: str | None = None,
    ) -> Select[tuple[SystemIncident]]:
        query = select(SystemIncident)
        severity_value = _enum_value(severity)
        status_value = _enum_value(status)

        if title is not None:
            query = query.where(SystemIncident.title == title)
        if severity_value is not None:
            query = query.where(SystemIncident.severity == severity_value)
        if status_value is not None:
            query = query.where(SystemIncident.status == status_value)
        if source is not None:
            query = query.where(SystemIncident.source == source)
        if component is not None:
            query = query.where(SystemIncident.component == component)
        if detected_from is not None:
            query = query.where(SystemIncident.detected_at >= detected_from)
        if detected_to is not None:
            query = query.where(SystemIncident.detected_at <= detected_to)
        if resolved_from is not None:
            query = query.where(SystemIncident.resolved_at >= resolved_from)
        if resolved_to is not None:
            query = query.where(SystemIncident.resolved_at <= resolved_to)
        if created_from is not None:
            query = query.where(SystemIncident.created_at >= created_from)
        if created_to is not None:
            query = query.where(SystemIncident.created_at <= created_to)
        if search is not None:
            term = f"%{search}%"
            query = query.where(
                or_(
                    SystemIncident.title.ilike(term),
                    SystemIncident.description.ilike(term),
                    SystemIncident.resolution_summary.ilike(term),
                    SystemIncident.source.ilike(term),
                    SystemIncident.component.ilike(term),
                ),
            )

        return query


class MonitoringHealthRepository:
    """Persistence boundary for monitoring and health data."""

    def __init__(self, db: Session) -> None:
        self.db = db
        self.health_checks = HealthCheckRecordRepository(db)
        self.metrics = MonitoringMetricRepository(db)
        self.incidents = SystemIncidentRepository(db)

    def health(self) -> bool:
        """Return whether all monitoring persistence boundaries are available."""

        return (
            self.health_checks.health()
            and self.metrics.health()
            and self.incidents.health()
        )

    def health_check(self) -> bool:
        """Return whether all monitoring persistence boundaries are available."""

        return self.health()


__all__ = [
    "HealthCheckRecordRepository",
    "MonitoringHealthRepository",
    "MonitoringMetricRepository",
    "SystemIncidentRepository",
]
