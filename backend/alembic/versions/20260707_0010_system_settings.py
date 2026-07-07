"""Create system settings schema.

Revision ID: 20260707_0010
Revises: 20260706_0009
Create Date: 2026-07-07 00:00:00.000000
"""

from __future__ import annotations

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision: str = "20260707_0010"
down_revision: str | None = "20260706_0009"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


json_type = postgresql.JSONB().with_variant(sa.JSON(), "sqlite")


def upgrade() -> None:
    op.create_table(
        "system_settings",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("uuid", sa.Uuid(as_uuid=True), nullable=False),
        sa.Column("category", sa.String(length=120), nullable=False),
        sa.Column("key", sa.String(length=160), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("value", json_type, nullable=True),
        sa.Column("default_value", json_type, nullable=True),
        sa.Column("value_type", sa.String(length=40), nullable=False),
        sa.Column("validation_rules", json_type, nullable=True),
        sa.Column("metadata", json_type, nullable=True),
        sa.Column("status", sa.String(length=40), nullable=False),
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
            name=op.f("fk_system_settings_created_by_id_users"),
        ),
        sa.ForeignKeyConstraint(
            ["deleted_by_id"],
            ["users.id"],
            name=op.f("fk_system_settings_deleted_by_id_users"),
        ),
        sa.ForeignKeyConstraint(
            ["updated_by_id"],
            ["users.id"],
            name=op.f("fk_system_settings_updated_by_id_users"),
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_system_settings")),
        sa.UniqueConstraint(
            "category",
            "key",
            name=op.f("uq_system_settings_category_key"),
        ),
    )
    for column, unique in (
        ("category", False),
        ("created_at", False),
        ("created_by_id", False),
        ("deleted_at", False),
        ("deleted_by_id", False),
        ("key", False),
        ("status", False),
        ("updated_by_id", False),
        ("uuid", True),
        ("value_type", False),
    ):
        op.create_index(
            op.f(f"ix_system_settings_{column}"),
            "system_settings",
            [column],
            unique=unique,
        )
    op.create_index(
        "ix_system_settings_category_key",
        "system_settings",
        ["category", "key"],
        unique=False,
    )

    op.create_table(
        "system_setting_defaults",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("uuid", sa.Uuid(as_uuid=True), nullable=False),
        sa.Column("category", sa.String(length=120), nullable=False),
        sa.Column("key", sa.String(length=160), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("default_value", json_type, nullable=True),
        sa.Column("value_type", sa.String(length=40), nullable=False),
        sa.Column("validation_rules", json_type, nullable=True),
        sa.Column("status", sa.String(length=40), nullable=False),
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
        sa.PrimaryKeyConstraint("id", name=op.f("pk_system_setting_defaults")),
        sa.UniqueConstraint(
            "category",
            "key",
            name=op.f("uq_system_setting_defaults_category_key"),
        ),
    )
    for column, unique in (
        ("category", False),
        ("created_at", False),
        ("key", False),
        ("status", False),
        ("uuid", True),
        ("value_type", False),
    ):
        op.create_index(
            op.f(f"ix_system_setting_defaults_{column}"),
            "system_setting_defaults",
            [column],
            unique=unique,
        )
    op.create_index(
        "ix_system_setting_defaults_category_key",
        "system_setting_defaults",
        ["category", "key"],
        unique=False,
    )

    op.create_table(
        "system_setting_change_events",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("event_uuid", sa.Uuid(as_uuid=True), nullable=False),
        sa.Column("system_setting_id", sa.Integer(), nullable=True),
        sa.Column("category", sa.String(length=120), nullable=False),
        sa.Column("key", sa.String(length=160), nullable=False),
        sa.Column("action", sa.String(length=80), nullable=False),
        sa.Column("old_value", json_type, nullable=True),
        sa.Column("new_value", json_type, nullable=True),
        sa.Column("actor_user_id", sa.Integer(), nullable=True),
        sa.Column("reason", sa.Text(), nullable=True),
        sa.Column("source", sa.String(length=120), nullable=True),
        sa.Column("request_id", sa.String(length=120), nullable=True),
        sa.Column("correlation_id", sa.String(length=120), nullable=True),
        sa.Column("metadata", json_type, nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["actor_user_id"],
            ["users.id"],
            name=op.f("fk_system_setting_change_events_actor_user_id_users"),
        ),
        sa.ForeignKeyConstraint(
            ["system_setting_id"],
            ["system_settings.id"],
            name=op.f("fk_system_setting_change_events_system_setting_id_system_settings"),
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_system_setting_change_events")),
    )
    for column, unique in (
        ("action", False),
        ("actor_user_id", False),
        ("category", False),
        ("correlation_id", False),
        ("created_at", False),
        ("event_uuid", True),
        ("key", False),
        ("request_id", False),
        ("source", False),
        ("system_setting_id", False),
    ):
        op.create_index(
            op.f(f"ix_system_setting_change_events_{column}"),
            "system_setting_change_events",
            [column],
            unique=unique,
        )
    op.create_index(
        "ix_system_setting_events_category_key",
        "system_setting_change_events",
        ["category", "key"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(
        "ix_system_setting_events_category_key",
        table_name="system_setting_change_events",
    )
    for column in (
        "system_setting_id",
        "source",
        "request_id",
        "key",
        "event_uuid",
        "created_at",
        "correlation_id",
        "category",
        "actor_user_id",
        "action",
    ):
        op.drop_index(
            op.f(f"ix_system_setting_change_events_{column}"),
            table_name="system_setting_change_events",
        )
    op.drop_table("system_setting_change_events")

    op.drop_index(
        "ix_system_setting_defaults_category_key",
        table_name="system_setting_defaults",
    )
    for column in (
        "value_type",
        "uuid",
        "status",
        "key",
        "created_at",
        "category",
    ):
        op.drop_index(
            op.f(f"ix_system_setting_defaults_{column}"),
            table_name="system_setting_defaults",
        )
    op.drop_table("system_setting_defaults")

    op.drop_index("ix_system_settings_category_key", table_name="system_settings")
    for column in (
        "value_type",
        "uuid",
        "updated_by_id",
        "status",
        "key",
        "deleted_by_id",
        "deleted_at",
        "created_by_id",
        "created_at",
        "category",
    ):
        op.drop_index(
            op.f(f"ix_system_settings_{column}"),
            table_name="system_settings",
        )
    op.drop_table("system_settings")
