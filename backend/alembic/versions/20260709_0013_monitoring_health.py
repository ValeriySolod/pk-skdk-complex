"""Create monitoring and health schema.

Revision ID: 20260709_0013
Revises: 20260708_0012
Create Date: 2026-07-09 00:00:00.000000
"""

from __future__ import annotations

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision: str = "20260709_0013"
down_revision: str | None = "20260708_0012"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


json_type = postgresql.JSONB().with_variant(sa.JSON(), "sqlite")


def upgrade() -> None:
    op.create_table(
        "health_check_records",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("record_uuid", sa.Uuid(as_uuid=True), nullable=False),
        sa.Column("component", sa.String(length=120), nullable=False),
        sa.Column("status", sa.String(length=40), nullable=False),
        sa.Column("response_time_ms", sa.Float(), nullable=True),
        sa.Column("message", sa.Text(), nullable=True),
        sa.Column("details", json_type, nullable=True),
        sa.Column(
            "checked_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_health_check_records")),
    )
    for column, unique in (
        ("checked_at", False),
        ("component", False),
        ("created_at", False),
        ("record_uuid", True),
        ("status", False),
    ):
        op.create_index(
            op.f(f"ix_health_check_records_{column}"),
            "health_check_records",
            [column],
            unique=unique,
        )
    op.create_index(
        "ix_health_check_records_component_status",
        "health_check_records",
        ["component", "status"],
        unique=False,
    )

    op.create_table(
        "monitoring_metrics",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("metric_uuid", sa.Uuid(as_uuid=True), nullable=False),
        sa.Column("metric_name", sa.String(length=160), nullable=False),
        sa.Column("category", sa.String(length=80), nullable=False),
        sa.Column("source", sa.String(length=120), nullable=True),
        sa.Column("value", sa.Float(), nullable=False),
        sa.Column("unit", sa.String(length=40), nullable=True),
        sa.Column("labels", json_type, nullable=True),
        sa.Column("details", json_type, nullable=True),
        sa.Column(
            "recorded_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_monitoring_metrics")),
    )
    for column, unique in (
        ("category", False),
        ("created_at", False),
        ("metric_name", False),
        ("metric_uuid", True),
        ("recorded_at", False),
        ("source", False),
    ):
        op.create_index(
            op.f(f"ix_monitoring_metrics_{column}"),
            "monitoring_metrics",
            [column],
            unique=unique,
        )
    op.create_index(
        "ix_monitoring_metrics_category_source",
        "monitoring_metrics",
        ["category", "source"],
        unique=False,
    )
    op.create_index(
        "ix_monitoring_metrics_name_recorded_at",
        "monitoring_metrics",
        ["metric_name", "recorded_at"],
        unique=False,
    )

    op.create_table(
        "system_incidents",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("incident_uuid", sa.Uuid(as_uuid=True), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("severity", sa.String(length=40), nullable=False),
        sa.Column("status", sa.String(length=40), nullable=False),
        sa.Column("source", sa.String(length=120), nullable=True),
        sa.Column("component", sa.String(length=120), nullable=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("resolution_summary", sa.Text(), nullable=True),
        sa.Column("metadata", json_type, nullable=True),
        sa.Column(
            "detected_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column("resolved_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_system_incidents")),
    )
    for column, unique in (
        ("component", False),
        ("created_at", False),
        ("detected_at", False),
        ("incident_uuid", True),
        ("resolved_at", False),
        ("severity", False),
        ("source", False),
        ("status", False),
        ("title", False),
    ):
        op.create_index(
            op.f(f"ix_system_incidents_{column}"),
            "system_incidents",
            [column],
            unique=unique,
        )
    op.create_index(
        "ix_system_incidents_severity_status",
        "system_incidents",
        ["severity", "status"],
        unique=False,
    )
    op.create_index(
        "ix_system_incidents_source_status",
        "system_incidents",
        ["source", "status"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("ix_system_incidents_source_status", table_name="system_incidents")
    op.drop_index("ix_system_incidents_severity_status", table_name="system_incidents")
    for column in (
        "title",
        "status",
        "source",
        "severity",
        "resolved_at",
        "incident_uuid",
        "detected_at",
        "created_at",
        "component",
    ):
        op.drop_index(
            op.f(f"ix_system_incidents_{column}"),
            table_name="system_incidents",
        )
    op.drop_table("system_incidents")

    op.drop_index(
        "ix_monitoring_metrics_name_recorded_at",
        table_name="monitoring_metrics",
    )
    op.drop_index(
        "ix_monitoring_metrics_category_source",
        table_name="monitoring_metrics",
    )
    for column in (
        "source",
        "recorded_at",
        "metric_uuid",
        "metric_name",
        "created_at",
        "category",
    ):
        op.drop_index(
            op.f(f"ix_monitoring_metrics_{column}"),
            table_name="monitoring_metrics",
        )
    op.drop_table("monitoring_metrics")

    op.drop_index(
        "ix_health_check_records_component_status",
        table_name="health_check_records",
    )
    for column in (
        "status",
        "record_uuid",
        "created_at",
        "component",
        "checked_at",
    ):
        op.drop_index(
            op.f(f"ix_health_check_records_{column}"),
            table_name="health_check_records",
        )
    op.drop_table("health_check_records")
