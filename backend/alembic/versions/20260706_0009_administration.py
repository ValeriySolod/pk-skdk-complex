"""Create administration schema.

Revision ID: 20260706_0009
Revises: 20260706_0008
Create Date: 2026-07-06 00:00:00.000000
"""

from __future__ import annotations

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision: str = "20260706_0009"
down_revision: str | None = "20260706_0008"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "administration_references",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("reference_uuid", sa.Uuid(as_uuid=True), nullable=False),
        sa.Column("catalog", sa.String(length=120), nullable=False),
        sa.Column("code", sa.String(length=120), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("status", sa.String(length=40), nullable=False),
        sa.Column(
            "metadata",
            postgresql.JSONB().with_variant(sa.JSON(), "sqlite"),
            nullable=True,
        ),
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
        sa.PrimaryKeyConstraint("id", name=op.f("pk_administration_references")),
        sa.UniqueConstraint("code", name=op.f("uq_administration_references_code")),
    )
    op.create_index(
        op.f("ix_administration_references_catalog"),
        "administration_references",
        ["catalog"],
        unique=False,
    )
    op.create_index(
        op.f("ix_administration_references_created_at"),
        "administration_references",
        ["created_at"],
        unique=False,
    )
    op.create_index(
        op.f("ix_administration_references_deleted_at"),
        "administration_references",
        ["deleted_at"],
        unique=False,
    )
    op.create_index(
        op.f("ix_administration_references_reference_uuid"),
        "administration_references",
        ["reference_uuid"],
        unique=True,
    )
    op.create_index(
        op.f("ix_administration_references_status"),
        "administration_references",
        ["status"],
        unique=False,
    )

    op.create_table(
        "administration_maintenance_tasks",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("task_uuid", sa.Uuid(as_uuid=True), nullable=False),
        sa.Column("operation_type", sa.String(length=120), nullable=False),
        sa.Column("operation_name", sa.String(length=255), nullable=False),
        sa.Column("status", sa.String(length=40), nullable=False),
        sa.Column("requested_by_user_id", sa.Integer(), nullable=True),
        sa.Column(
            "payload",
            postgresql.JSONB().with_variant(sa.JSON(), "sqlite"),
            nullable=True,
        ),
        sa.Column(
            "result",
            postgresql.JSONB().with_variant(sa.JSON(), "sqlite"),
            nullable=True,
        ),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column(
            "requested_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
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
            ["requested_by_user_id"],
            ["users.id"],
            name=op.f("fk_administration_maintenance_tasks_requested_by_user_id_users"),
        ),
        sa.PrimaryKeyConstraint(
            "id",
            name=op.f("pk_administration_maintenance_tasks"),
        ),
    )
    for column, unique in (
        ("completed_at", False),
        ("created_at", False),
        ("deleted_at", False),
        ("operation_type", False),
        ("requested_at", False),
        ("requested_by_user_id", False),
        ("started_at", False),
        ("status", False),
        ("task_uuid", True),
    ):
        op.create_index(
            op.f(f"ix_administration_maintenance_tasks_{column}"),
            "administration_maintenance_tasks",
            [column],
            unique=unique,
        )

    op.create_table(
        "administration_action_events",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("event_uuid", sa.Uuid(as_uuid=True), nullable=False),
        sa.Column("action_type", sa.String(length=120), nullable=False),
        sa.Column("status", sa.String(length=40), nullable=False),
        sa.Column("target_type", sa.String(length=120), nullable=True),
        sa.Column("target_id", sa.String(length=120), nullable=True),
        sa.Column("resource", sa.String(length=255), nullable=True),
        sa.Column("actor_user_id", sa.Integer(), nullable=True),
        sa.Column("actor_username", sa.String(length=255), nullable=True),
        sa.Column("correlation_id", sa.String(length=120), nullable=True),
        sa.Column("request_id", sa.String(length=120), nullable=True),
        sa.Column(
            "details",
            postgresql.JSONB().with_variant(sa.JSON(), "sqlite"),
            nullable=False,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["actor_user_id"],
            ["users.id"],
            name=op.f("fk_administration_action_events_actor_user_id_users"),
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_administration_action_events")),
    )
    for column, unique in (
        ("action_type", False),
        ("actor_user_id", False),
        ("correlation_id", False),
        ("created_at", False),
        ("event_uuid", True),
        ("request_id", False),
        ("status", False),
        ("target_id", False),
        ("target_type", False),
    ):
        op.create_index(
            op.f(f"ix_administration_action_events_{column}"),
            "administration_action_events",
            [column],
            unique=unique,
        )


def downgrade() -> None:
    for column in (
        "target_type",
        "target_id",
        "status",
        "request_id",
        "event_uuid",
        "created_at",
        "correlation_id",
        "actor_user_id",
        "action_type",
    ):
        op.drop_index(
            op.f(f"ix_administration_action_events_{column}"),
            table_name="administration_action_events",
        )
    op.drop_table("administration_action_events")

    for column in (
        "task_uuid",
        "status",
        "started_at",
        "requested_by_user_id",
        "requested_at",
        "operation_type",
        "deleted_at",
        "created_at",
        "completed_at",
    ):
        op.drop_index(
            op.f(f"ix_administration_maintenance_tasks_{column}"),
            table_name="administration_maintenance_tasks",
        )
    op.drop_table("administration_maintenance_tasks")

    op.drop_index(
        op.f("ix_administration_references_status"),
        table_name="administration_references",
    )
    op.drop_index(
        op.f("ix_administration_references_reference_uuid"),
        table_name="administration_references",
    )
    op.drop_index(
        op.f("ix_administration_references_deleted_at"),
        table_name="administration_references",
    )
    op.drop_index(
        op.f("ix_administration_references_created_at"),
        table_name="administration_references",
    )
    op.drop_index(
        op.f("ix_administration_references_catalog"),
        table_name="administration_references",
    )
    op.drop_table("administration_references")
