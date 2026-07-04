"""Create user management schema.

Revision ID: 20260704_0003
Revises: 20260704_0002
Create Date: 2026-07-04 00:00:00.000000
"""

from __future__ import annotations

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision: str = "20260704_0003"
down_revision: str | None = "20260704_0002"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "user_management_profiles",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("display_name", sa.String(length=255), nullable=True),
        sa.Column("personnel_number", sa.String(length=80), nullable=True),
        sa.Column("job_title", sa.String(length=255), nullable=True),
        sa.Column("phone_number", sa.String(length=80), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("notes", sa.Text(), nullable=True),
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
            ["user_id"],
            ["users.id"],
            name=op.f("fk_user_management_profiles_user_id_users"),
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_user_management_profiles")),
        sa.UniqueConstraint(
            "user_id",
            name=op.f("uq_user_management_profiles_user_id"),
        ),
    )
    op.create_index(
        op.f("ix_user_management_profiles_is_active"),
        "user_management_profiles",
        ["is_active"],
        unique=False,
    )
    op.create_index(
        op.f("ix_user_management_profiles_personnel_number"),
        "user_management_profiles",
        ["personnel_number"],
        unique=False,
    )
    op.create_index(
        op.f("ix_user_management_profiles_user_id"),
        "user_management_profiles",
        ["user_id"],
        unique=False,
    )

    op.create_table(
        "user_management_role_assignments",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("role_code", sa.String(length=120), nullable=False),
        sa.Column("scope_type", sa.String(length=80), nullable=True),
        sa.Column("scope_id", sa.Integer(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("assigned_by_user_id", sa.Integer(), nullable=True),
        sa.Column(
            "assigned_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column("revoked_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(
            ["assigned_by_user_id"],
            ["users.id"],
            name=op.f("fk_user_management_role_assignments_assigned_by_user_id_users"),
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            name=op.f("fk_user_management_role_assignments_user_id_users"),
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_user_management_role_assignments")),
        sa.UniqueConstraint(
            "user_id",
            "role_code",
            "scope_type",
            "scope_id",
            name="uq_user_management_role_assignment_scope",
        ),
    )
    op.create_index(
        op.f("ix_user_management_role_assignments_is_active"),
        "user_management_role_assignments",
        ["is_active"],
        unique=False,
    )
    op.create_index(
        op.f("ix_user_management_role_assignments_role_code"),
        "user_management_role_assignments",
        ["role_code"],
        unique=False,
    )
    op.create_index(
        op.f("ix_user_management_role_assignments_scope_id"),
        "user_management_role_assignments",
        ["scope_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_user_management_role_assignments_scope_type"),
        "user_management_role_assignments",
        ["scope_type"],
        unique=False,
    )
    op.create_index(
        op.f("ix_user_management_role_assignments_user_id"),
        "user_management_role_assignments",
        ["user_id"],
        unique=False,
    )

    op.create_table(
        "user_management_audit_events",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("actor_user_id", sa.Integer(), nullable=True),
        sa.Column("target_user_id", sa.Integer(), nullable=True),
        sa.Column("event_type", sa.String(length=120), nullable=False),
        sa.Column("summary", sa.String(length=255), nullable=True),
        sa.Column(
            "details",
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
            name=op.f("fk_user_management_audit_events_actor_user_id_users"),
        ),
        sa.ForeignKeyConstraint(
            ["target_user_id"],
            ["users.id"],
            name=op.f("fk_user_management_audit_events_target_user_id_users"),
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_user_management_audit_events")),
    )
    op.create_index(
        op.f("ix_user_management_audit_events_actor_user_id"),
        "user_management_audit_events",
        ["actor_user_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_user_management_audit_events_created_at"),
        "user_management_audit_events",
        ["created_at"],
        unique=False,
    )
    op.create_index(
        op.f("ix_user_management_audit_events_event_type"),
        "user_management_audit_events",
        ["event_type"],
        unique=False,
    )
    op.create_index(
        op.f("ix_user_management_audit_events_target_user_id"),
        "user_management_audit_events",
        ["target_user_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(
        op.f("ix_user_management_audit_events_target_user_id"),
        table_name="user_management_audit_events",
    )
    op.drop_index(
        op.f("ix_user_management_audit_events_event_type"),
        table_name="user_management_audit_events",
    )
    op.drop_index(
        op.f("ix_user_management_audit_events_created_at"),
        table_name="user_management_audit_events",
    )
    op.drop_index(
        op.f("ix_user_management_audit_events_actor_user_id"),
        table_name="user_management_audit_events",
    )
    op.drop_table("user_management_audit_events")

    op.drop_index(
        op.f("ix_user_management_role_assignments_user_id"),
        table_name="user_management_role_assignments",
    )
    op.drop_index(
        op.f("ix_user_management_role_assignments_scope_type"),
        table_name="user_management_role_assignments",
    )
    op.drop_index(
        op.f("ix_user_management_role_assignments_scope_id"),
        table_name="user_management_role_assignments",
    )
    op.drop_index(
        op.f("ix_user_management_role_assignments_role_code"),
        table_name="user_management_role_assignments",
    )
    op.drop_index(
        op.f("ix_user_management_role_assignments_is_active"),
        table_name="user_management_role_assignments",
    )
    op.drop_table("user_management_role_assignments")

    op.drop_index(
        op.f("ix_user_management_profiles_user_id"),
        table_name="user_management_profiles",
    )
    op.drop_index(
        op.f("ix_user_management_profiles_personnel_number"),
        table_name="user_management_profiles",
    )
    op.drop_index(
        op.f("ix_user_management_profiles_is_active"),
        table_name="user_management_profiles",
    )
    op.drop_table("user_management_profiles")
