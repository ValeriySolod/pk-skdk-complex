"""Create integrations schema.

Revision ID: 20260708_0011
Revises: 20260707_0010
Create Date: 2026-07-08 00:00:00.000000
"""

from __future__ import annotations

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision: str = "20260708_0011"
down_revision: str | None = "20260707_0010"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


json_type = postgresql.JSONB().with_variant(sa.JSON(), "sqlite")


def upgrade() -> None:
    op.create_table(
        "integration_providers",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("provider_uuid", sa.Uuid(as_uuid=True), nullable=False),
        sa.Column("code", sa.String(length=120), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("provider_type", sa.String(length=80), nullable=False),
        sa.Column("status", sa.String(length=40), nullable=False),
        sa.Column("auth_type", sa.String(length=80), nullable=True),
        sa.Column("base_url", sa.String(length=1024), nullable=True),
        sa.Column("capabilities", json_type, nullable=True),
        sa.Column("default_config", json_type, nullable=True),
        sa.Column("metadata", json_type, nullable=True),
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
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_integration_providers")),
        sa.UniqueConstraint("code", name=op.f("uq_integration_providers_code")),
    )
    for column, unique in (
        ("auth_type", False),
        ("code", False),
        ("created_at", False),
        ("deleted_at", False),
        ("provider_type", False),
        ("provider_uuid", True),
        ("status", False),
    ):
        op.create_index(
            op.f(f"ix_integration_providers_{column}"),
            "integration_providers",
            [column],
            unique=unique,
        )

    op.create_table(
        "integration_connections",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("connection_uuid", sa.Uuid(as_uuid=True), nullable=False),
        sa.Column("provider_id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("status", sa.String(length=40), nullable=False),
        sa.Column("environment", sa.String(length=80), nullable=True),
        sa.Column("external_account_id", sa.String(length=255), nullable=True),
        sa.Column("config", json_type, nullable=True),
        sa.Column("credentials_ref", sa.String(length=255), nullable=True),
        sa.Column("sync_settings", json_type, nullable=True),
        sa.Column("metadata", json_type, nullable=True),
        sa.Column("last_sync_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("last_error_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("last_error_message", sa.Text(), nullable=True),
        sa.Column("created_by_id", sa.Integer(), nullable=True),
        sa.Column("updated_by_id", sa.Integer(), nullable=True),
        sa.Column("deleted_by_id", sa.Integer(), nullable=True),
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
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(
            ["created_by_id"],
            ["users.id"],
            name=op.f("fk_integration_connections_created_by_id_users"),
        ),
        sa.ForeignKeyConstraint(
            ["deleted_by_id"],
            ["users.id"],
            name=op.f("fk_integration_connections_deleted_by_id_users"),
        ),
        sa.ForeignKeyConstraint(
            ["provider_id"],
            ["integration_providers.id"],
            name=op.f("fk_integration_connections_provider_id_integration_providers"),
        ),
        sa.ForeignKeyConstraint(
            ["updated_by_id"],
            ["users.id"],
            name=op.f("fk_integration_connections_updated_by_id_users"),
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_integration_connections")),
        sa.UniqueConstraint(
            "provider_id",
            "name",
            name=op.f("uq_integration_connections_provider_name"),
        ),
    )
    for column, unique in (
        ("connection_uuid", True),
        ("created_at", False),
        ("created_by_id", False),
        ("deleted_at", False),
        ("deleted_by_id", False),
        ("environment", False),
        ("external_account_id", False),
        ("last_sync_at", False),
        ("name", False),
        ("provider_id", False),
        ("status", False),
        ("updated_by_id", False),
    ):
        op.create_index(
            op.f(f"ix_integration_connections_{column}"),
            "integration_connections",
            [column],
            unique=unique,
        )
    op.create_index(
        "ix_integration_connections_uuid_name_provider",
        "integration_connections",
        ["connection_uuid", "name", "provider_id"],
        unique=False,
    )

    op.create_table(
        "integration_sync_jobs",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("job_uuid", sa.Uuid(as_uuid=True), nullable=False),
        sa.Column("connection_id", sa.Integer(), nullable=False),
        sa.Column("sync_type", sa.String(length=120), nullable=False),
        sa.Column("direction", sa.String(length=40), nullable=True),
        sa.Column("status", sa.String(length=40), nullable=False),
        sa.Column("request_payload", json_type, nullable=True),
        sa.Column("result_summary", json_type, nullable=True),
        sa.Column("records_processed", sa.Integer(), nullable=False),
        sa.Column("records_succeeded", sa.Integer(), nullable=False),
        sa.Column("records_failed", sa.Integer(), nullable=False),
        sa.Column("scheduled_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("failed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("failure_reason", sa.Text(), nullable=True),
        sa.Column("triggered_by_user_id", sa.Integer(), nullable=True),
        sa.Column("correlation_id", sa.String(length=120), nullable=True),
        sa.Column("metadata", json_type, nullable=True),
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
        sa.ForeignKeyConstraint(
            ["connection_id"],
            ["integration_connections.id"],
            name=op.f("fk_integration_sync_jobs_connection_id_integration_connections"),
        ),
        sa.ForeignKeyConstraint(
            ["triggered_by_user_id"],
            ["users.id"],
            name=op.f("fk_integration_sync_jobs_triggered_by_user_id_users"),
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_integration_sync_jobs")),
    )
    for column, unique in (
        ("completed_at", False),
        ("connection_id", False),
        ("correlation_id", False),
        ("created_at", False),
        ("direction", False),
        ("job_uuid", True),
        ("scheduled_at", False),
        ("started_at", False),
        ("status", False),
        ("sync_type", False),
        ("triggered_by_user_id", False),
    ):
        op.create_index(
            op.f(f"ix_integration_sync_jobs_{column}"),
            "integration_sync_jobs",
            [column],
            unique=unique,
        )
    op.create_index(
        "ix_integration_sync_jobs_connection_status",
        "integration_sync_jobs",
        ["connection_id", "status"],
        unique=False,
    )

    op.create_table(
        "integration_events",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("event_uuid", sa.Uuid(as_uuid=True), nullable=False),
        sa.Column("connection_id", sa.Integer(), nullable=False),
        sa.Column("sync_job_id", sa.Integer(), nullable=True),
        sa.Column("event_type", sa.String(length=120), nullable=False),
        sa.Column("status", sa.String(length=40), nullable=False),
        sa.Column("source", sa.String(length=120), nullable=True),
        sa.Column("external_event_id", sa.String(length=255), nullable=True),
        sa.Column("entity_type", sa.String(length=120), nullable=True),
        sa.Column("entity_id", sa.String(length=120), nullable=True),
        sa.Column("payload", json_type, nullable=True),
        sa.Column("headers", json_type, nullable=True),
        sa.Column("processing_result", json_type, nullable=True),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column(
            "received_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column("processed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("correlation_id", sa.String(length=120), nullable=True),
        sa.Column("metadata", json_type, nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["connection_id"],
            ["integration_connections.id"],
            name=op.f("fk_integration_events_connection_id_integration_connections"),
        ),
        sa.ForeignKeyConstraint(
            ["sync_job_id"],
            ["integration_sync_jobs.id"],
            name=op.f("fk_integration_events_sync_job_id_integration_sync_jobs"),
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_integration_events")),
    )
    for column, unique in (
        ("connection_id", False),
        ("correlation_id", False),
        ("created_at", False),
        ("entity_id", False),
        ("entity_type", False),
        ("event_type", False),
        ("event_uuid", True),
        ("external_event_id", False),
        ("processed_at", False),
        ("received_at", False),
        ("source", False),
        ("status", False),
        ("sync_job_id", False),
    ):
        op.create_index(
            op.f(f"ix_integration_events_{column}"),
            "integration_events",
            [column],
            unique=unique,
        )
    op.create_index(
        "ix_integration_events_connection_event_type",
        "integration_events",
        ["connection_id", "event_type"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(
        "ix_integration_events_connection_event_type",
        table_name="integration_events",
    )
    for column in (
        "sync_job_id",
        "status",
        "source",
        "received_at",
        "processed_at",
        "external_event_id",
        "event_uuid",
        "event_type",
        "entity_type",
        "entity_id",
        "created_at",
        "correlation_id",
        "connection_id",
    ):
        op.drop_index(
            op.f(f"ix_integration_events_{column}"),
            table_name="integration_events",
        )
    op.drop_table("integration_events")

    op.drop_index(
        "ix_integration_sync_jobs_connection_status",
        table_name="integration_sync_jobs",
    )
    for column in (
        "triggered_by_user_id",
        "sync_type",
        "status",
        "started_at",
        "scheduled_at",
        "job_uuid",
        "direction",
        "created_at",
        "correlation_id",
        "connection_id",
        "completed_at",
    ):
        op.drop_index(
            op.f(f"ix_integration_sync_jobs_{column}"),
            table_name="integration_sync_jobs",
        )
    op.drop_table("integration_sync_jobs")

    op.drop_index(
        "ix_integration_connections_uuid_name_provider",
        table_name="integration_connections",
    )
    for column in (
        "updated_by_id",
        "status",
        "provider_id",
        "name",
        "last_sync_at",
        "external_account_id",
        "environment",
        "deleted_by_id",
        "deleted_at",
        "created_by_id",
        "created_at",
        "connection_uuid",
    ):
        op.drop_index(
            op.f(f"ix_integration_connections_{column}"),
            table_name="integration_connections",
        )
    op.drop_table("integration_connections")

    for column in (
        "status",
        "provider_uuid",
        "provider_type",
        "deleted_at",
        "created_at",
        "code",
        "auth_type",
    ):
        op.drop_index(
            op.f(f"ix_integration_providers_{column}"),
            table_name="integration_providers",
        )
    op.drop_table("integration_providers")
