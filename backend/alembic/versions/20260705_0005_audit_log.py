"""Create audit log schema.

Revision ID: 20260705_0005
Revises: 20260705_0004
Create Date: 2026-07-05 00:00:00.000000
"""

from __future__ import annotations

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision: str = "20260705_0005"
down_revision: str | None = "20260705_0004"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "audit_log_events",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("event_uuid", sa.Uuid(as_uuid=True), nullable=False),
        sa.Column("event_type", sa.String(length=120), nullable=False),
        sa.Column("entity_type", sa.String(length=120), nullable=True),
        sa.Column("entity_id", sa.String(length=120), nullable=True),
        sa.Column("actor_user_id", sa.Integer(), nullable=True),
        sa.Column("actor_username", sa.String(length=255), nullable=True),
        sa.Column("action", sa.String(length=120), nullable=False),
        sa.Column("status", sa.String(length=40), nullable=False),
        sa.Column("ip_address", sa.String(length=64), nullable=True),
        sa.Column("user_agent", sa.String(length=512), nullable=True),
        sa.Column("request_id", sa.String(length=120), nullable=True),
        sa.Column("correlation_id", sa.String(length=120), nullable=True),
        sa.Column(
            "payload",
            postgresql.JSONB().with_variant(sa.JSON(), "sqlite"),
            nullable=False,
        ),
        sa.Column(
            "before_state",
            postgresql.JSONB().with_variant(sa.JSON(), "sqlite"),
            nullable=True,
        ),
        sa.Column(
            "after_state",
            postgresql.JSONB().with_variant(sa.JSON(), "sqlite"),
            nullable=True,
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
            name=op.f("fk_audit_log_events_actor_user_id_users"),
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_audit_log_events")),
    )
    op.create_index(
        op.f("ix_audit_log_events_action"),
        "audit_log_events",
        ["action"],
        unique=False,
    )
    op.create_index(
        op.f("ix_audit_log_events_actor_user_id"),
        "audit_log_events",
        ["actor_user_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_audit_log_events_correlation_id"),
        "audit_log_events",
        ["correlation_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_audit_log_events_created_at"),
        "audit_log_events",
        ["created_at"],
        unique=False,
    )
    op.create_index(
        op.f("ix_audit_log_events_entity_id"),
        "audit_log_events",
        ["entity_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_audit_log_events_entity_type"),
        "audit_log_events",
        ["entity_type"],
        unique=False,
    )
    op.create_index(
        op.f("ix_audit_log_events_event_type"),
        "audit_log_events",
        ["event_type"],
        unique=False,
    )
    op.create_index(
        op.f("ix_audit_log_events_event_uuid"),
        "audit_log_events",
        ["event_uuid"],
        unique=True,
    )
    op.create_index(
        op.f("ix_audit_log_events_request_id"),
        "audit_log_events",
        ["request_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(
        op.f("ix_audit_log_events_request_id"),
        table_name="audit_log_events",
    )
    op.drop_index(
        op.f("ix_audit_log_events_event_uuid"),
        table_name="audit_log_events",
    )
    op.drop_index(
        op.f("ix_audit_log_events_event_type"),
        table_name="audit_log_events",
    )
    op.drop_index(
        op.f("ix_audit_log_events_entity_type"),
        table_name="audit_log_events",
    )
    op.drop_index(
        op.f("ix_audit_log_events_entity_id"),
        table_name="audit_log_events",
    )
    op.drop_index(
        op.f("ix_audit_log_events_created_at"),
        table_name="audit_log_events",
    )
    op.drop_index(
        op.f("ix_audit_log_events_correlation_id"),
        table_name="audit_log_events",
    )
    op.drop_index(
        op.f("ix_audit_log_events_actor_user_id"),
        table_name="audit_log_events",
    )
    op.drop_index(
        op.f("ix_audit_log_events_action"),
        table_name="audit_log_events",
    )
    op.drop_table("audit_log_events")
