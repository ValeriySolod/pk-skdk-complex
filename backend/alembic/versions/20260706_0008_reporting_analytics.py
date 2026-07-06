"""Create reporting analytics schema.

Revision ID: 20260706_0008
Revises: 20260705_0007
Create Date: 2026-07-06 00:00:00.000000
"""

from __future__ import annotations

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision: str = "20260706_0008"
down_revision: str | None = "20260705_0007"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "analytics_dashboard_definitions",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("dashboard_uuid", sa.Uuid(as_uuid=True), nullable=False),
        sa.Column("code", sa.String(length=120), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("category", sa.String(length=120), nullable=True),
        sa.Column("status", sa.String(length=40), nullable=False),
        sa.Column("owner_user_id", sa.Integer(), nullable=True),
        sa.Column(
            "layout_config",
            postgresql.JSONB().with_variant(sa.JSON(), "sqlite"),
            nullable=True,
        ),
        sa.Column(
            "widget_config",
            postgresql.JSONB().with_variant(sa.JSON(), "sqlite"),
            nullable=True,
        ),
        sa.Column(
            "filter_config",
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
        sa.ForeignKeyConstraint(
            ["owner_user_id"],
            ["users.id"],
            name=op.f("fk_analytics_dashboard_definitions_owner_user_id_users"),
        ),
        sa.PrimaryKeyConstraint(
            "id",
            name=op.f("pk_analytics_dashboard_definitions"),
        ),
        sa.UniqueConstraint(
            "code",
            name=op.f("uq_analytics_dashboard_definitions_code"),
        ),
    )
    op.create_index(
        op.f("ix_analytics_dashboard_definitions_category"),
        "analytics_dashboard_definitions",
        ["category"],
        unique=False,
    )
    op.create_index(
        op.f("ix_analytics_dashboard_definitions_created_at"),
        "analytics_dashboard_definitions",
        ["created_at"],
        unique=False,
    )
    op.create_index(
        op.f("ix_analytics_dashboard_definitions_dashboard_uuid"),
        "analytics_dashboard_definitions",
        ["dashboard_uuid"],
        unique=True,
    )
    op.create_index(
        op.f("ix_analytics_dashboard_definitions_deleted_at"),
        "analytics_dashboard_definitions",
        ["deleted_at"],
        unique=False,
    )
    op.create_index(
        op.f("ix_analytics_dashboard_definitions_owner_user_id"),
        "analytics_dashboard_definitions",
        ["owner_user_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_analytics_dashboard_definitions_status"),
        "analytics_dashboard_definitions",
        ["status"],
        unique=False,
    )

    op.create_table(
        "analytics_report_definitions",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("report_uuid", sa.Uuid(as_uuid=True), nullable=False),
        sa.Column("code", sa.String(length=120), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("category", sa.String(length=120), nullable=True),
        sa.Column("source_module", sa.String(length=120), nullable=True),
        sa.Column("status", sa.String(length=40), nullable=False),
        sa.Column("default_format", sa.String(length=20), nullable=False),
        sa.Column("owner_user_id", sa.Integer(), nullable=True),
        sa.Column(
            "query_config",
            postgresql.JSONB().with_variant(sa.JSON(), "sqlite"),
            nullable=True,
        ),
        sa.Column(
            "filter_schema",
            postgresql.JSONB().with_variant(sa.JSON(), "sqlite"),
            nullable=True,
        ),
        sa.Column(
            "layout_config",
            postgresql.JSONB().with_variant(sa.JSON(), "sqlite"),
            nullable=True,
        ),
        sa.Column("last_generated_at", sa.DateTime(timezone=True), nullable=True),
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
            ["owner_user_id"],
            ["users.id"],
            name=op.f("fk_analytics_report_definitions_owner_user_id_users"),
        ),
        sa.PrimaryKeyConstraint(
            "id",
            name=op.f("pk_analytics_report_definitions"),
        ),
        sa.UniqueConstraint(
            "code",
            name=op.f("uq_analytics_report_definitions_code"),
        ),
    )
    op.create_index(
        op.f("ix_analytics_report_definitions_category"),
        "analytics_report_definitions",
        ["category"],
        unique=False,
    )
    op.create_index(
        op.f("ix_analytics_report_definitions_created_at"),
        "analytics_report_definitions",
        ["created_at"],
        unique=False,
    )
    op.create_index(
        op.f("ix_analytics_report_definitions_default_format"),
        "analytics_report_definitions",
        ["default_format"],
        unique=False,
    )
    op.create_index(
        op.f("ix_analytics_report_definitions_deleted_at"),
        "analytics_report_definitions",
        ["deleted_at"],
        unique=False,
    )
    op.create_index(
        op.f("ix_analytics_report_definitions_last_generated_at"),
        "analytics_report_definitions",
        ["last_generated_at"],
        unique=False,
    )
    op.create_index(
        op.f("ix_analytics_report_definitions_owner_user_id"),
        "analytics_report_definitions",
        ["owner_user_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_analytics_report_definitions_report_uuid"),
        "analytics_report_definitions",
        ["report_uuid"],
        unique=True,
    )
    op.create_index(
        op.f("ix_analytics_report_definitions_source_module"),
        "analytics_report_definitions",
        ["source_module"],
        unique=False,
    )
    op.create_index(
        op.f("ix_analytics_report_definitions_status"),
        "analytics_report_definitions",
        ["status"],
        unique=False,
    )

    op.create_table(
        "analytics_report_runs",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("run_uuid", sa.Uuid(as_uuid=True), nullable=False),
        sa.Column("report_definition_id", sa.Integer(), nullable=False),
        sa.Column("requested_by_user_id", sa.Integer(), nullable=True),
        sa.Column("file_object_id", sa.Integer(), nullable=True),
        sa.Column("status", sa.String(length=40), nullable=False),
        sa.Column("output_format", sa.String(length=20), nullable=False),
        sa.Column(
            "parameters",
            postgresql.JSONB().with_variant(sa.JSON(), "sqlite"),
            nullable=True,
        ),
        sa.Column(
            "result_summary",
            postgresql.JSONB().with_variant(sa.JSON(), "sqlite"),
            nullable=True,
        ),
        sa.Column("row_count", sa.Integer(), nullable=False),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("failed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("failure_reason", sa.Text(), nullable=True),
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
            ["file_object_id"],
            ["file_storage_objects.id"],
            name=op.f("fk_analytics_report_runs_file_object_id_file_storage_objects"),
        ),
        sa.ForeignKeyConstraint(
            ["report_definition_id"],
            ["analytics_report_definitions.id"],
            name=op.f(
                "fk_analytics_report_runs_report_definition_id_analytics_report_definitions"
            ),
        ),
        sa.ForeignKeyConstraint(
            ["requested_by_user_id"],
            ["users.id"],
            name=op.f("fk_analytics_report_runs_requested_by_user_id_users"),
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_analytics_report_runs")),
    )
    op.create_index(
        op.f("ix_analytics_report_runs_completed_at"),
        "analytics_report_runs",
        ["completed_at"],
        unique=False,
    )
    op.create_index(
        op.f("ix_analytics_report_runs_created_at"),
        "analytics_report_runs",
        ["created_at"],
        unique=False,
    )
    op.create_index(
        op.f("ix_analytics_report_runs_file_object_id"),
        "analytics_report_runs",
        ["file_object_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_analytics_report_runs_output_format"),
        "analytics_report_runs",
        ["output_format"],
        unique=False,
    )
    op.create_index(
        op.f("ix_analytics_report_runs_report_definition_id"),
        "analytics_report_runs",
        ["report_definition_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_analytics_report_runs_requested_by_user_id"),
        "analytics_report_runs",
        ["requested_by_user_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_analytics_report_runs_run_uuid"),
        "analytics_report_runs",
        ["run_uuid"],
        unique=True,
    )
    op.create_index(
        op.f("ix_analytics_report_runs_started_at"),
        "analytics_report_runs",
        ["started_at"],
        unique=False,
    )
    op.create_index(
        op.f("ix_analytics_report_runs_status"),
        "analytics_report_runs",
        ["status"],
        unique=False,
    )

    op.create_table(
        "analytics_snapshots",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("snapshot_uuid", sa.Uuid(as_uuid=True), nullable=False),
        sa.Column("metric_key", sa.String(length=160), nullable=False),
        sa.Column("metric_name", sa.String(length=255), nullable=False),
        sa.Column("source_module", sa.String(length=120), nullable=True),
        sa.Column("entity_type", sa.String(length=120), nullable=True),
        sa.Column("entity_id", sa.String(length=120), nullable=True),
        sa.Column("period", sa.String(length=40), nullable=False),
        sa.Column("status", sa.String(length=40), nullable=False),
        sa.Column(
            "value",
            postgresql.JSONB().with_variant(sa.JSON(), "sqlite"),
            nullable=False,
        ),
        sa.Column(
            "dimensions",
            postgresql.JSONB().with_variant(sa.JSON(), "sqlite"),
            nullable=True,
        ),
        sa.Column("period_start", sa.DateTime(timezone=True), nullable=True),
        sa.Column("period_end", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "calculated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column("failure_reason", sa.Text(), nullable=True),
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
        sa.PrimaryKeyConstraint("id", name=op.f("pk_analytics_snapshots")),
    )
    op.create_index(
        op.f("ix_analytics_snapshots_calculated_at"),
        "analytics_snapshots",
        ["calculated_at"],
        unique=False,
    )
    op.create_index(
        op.f("ix_analytics_snapshots_created_at"),
        "analytics_snapshots",
        ["created_at"],
        unique=False,
    )
    op.create_index(
        op.f("ix_analytics_snapshots_entity_id"),
        "analytics_snapshots",
        ["entity_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_analytics_snapshots_entity_type"),
        "analytics_snapshots",
        ["entity_type"],
        unique=False,
    )
    op.create_index(
        op.f("ix_analytics_snapshots_metric_key"),
        "analytics_snapshots",
        ["metric_key"],
        unique=False,
    )
    op.create_index(
        op.f("ix_analytics_snapshots_period"),
        "analytics_snapshots",
        ["period"],
        unique=False,
    )
    op.create_index(
        op.f("ix_analytics_snapshots_period_end"),
        "analytics_snapshots",
        ["period_end"],
        unique=False,
    )
    op.create_index(
        op.f("ix_analytics_snapshots_period_start"),
        "analytics_snapshots",
        ["period_start"],
        unique=False,
    )
    op.create_index(
        op.f("ix_analytics_snapshots_snapshot_uuid"),
        "analytics_snapshots",
        ["snapshot_uuid"],
        unique=True,
    )
    op.create_index(
        op.f("ix_analytics_snapshots_source_module"),
        "analytics_snapshots",
        ["source_module"],
        unique=False,
    )
    op.create_index(
        op.f("ix_analytics_snapshots_status"),
        "analytics_snapshots",
        ["status"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(
        op.f("ix_analytics_snapshots_status"), table_name="analytics_snapshots"
    )
    op.drop_index(
        op.f("ix_analytics_snapshots_source_module"),
        table_name="analytics_snapshots",
    )
    op.drop_index(
        op.f("ix_analytics_snapshots_snapshot_uuid"),
        table_name="analytics_snapshots",
    )
    op.drop_index(
        op.f("ix_analytics_snapshots_period_start"),
        table_name="analytics_snapshots",
    )
    op.drop_index(
        op.f("ix_analytics_snapshots_period_end"),
        table_name="analytics_snapshots",
    )
    op.drop_index(
        op.f("ix_analytics_snapshots_period"), table_name="analytics_snapshots"
    )
    op.drop_index(
        op.f("ix_analytics_snapshots_metric_key"),
        table_name="analytics_snapshots",
    )
    op.drop_index(
        op.f("ix_analytics_snapshots_entity_type"),
        table_name="analytics_snapshots",
    )
    op.drop_index(
        op.f("ix_analytics_snapshots_entity_id"),
        table_name="analytics_snapshots",
    )
    op.drop_index(
        op.f("ix_analytics_snapshots_created_at"),
        table_name="analytics_snapshots",
    )
    op.drop_index(
        op.f("ix_analytics_snapshots_calculated_at"),
        table_name="analytics_snapshots",
    )
    op.drop_table("analytics_snapshots")

    op.drop_index(
        op.f("ix_analytics_report_runs_status"), table_name="analytics_report_runs"
    )
    op.drop_index(
        op.f("ix_analytics_report_runs_started_at"),
        table_name="analytics_report_runs",
    )
    op.drop_index(
        op.f("ix_analytics_report_runs_run_uuid"),
        table_name="analytics_report_runs",
    )
    op.drop_index(
        op.f("ix_analytics_report_runs_requested_by_user_id"),
        table_name="analytics_report_runs",
    )
    op.drop_index(
        op.f("ix_analytics_report_runs_report_definition_id"),
        table_name="analytics_report_runs",
    )
    op.drop_index(
        op.f("ix_analytics_report_runs_output_format"),
        table_name="analytics_report_runs",
    )
    op.drop_index(
        op.f("ix_analytics_report_runs_file_object_id"),
        table_name="analytics_report_runs",
    )
    op.drop_index(
        op.f("ix_analytics_report_runs_created_at"),
        table_name="analytics_report_runs",
    )
    op.drop_index(
        op.f("ix_analytics_report_runs_completed_at"),
        table_name="analytics_report_runs",
    )
    op.drop_table("analytics_report_runs")

    op.drop_index(
        op.f("ix_analytics_report_definitions_status"),
        table_name="analytics_report_definitions",
    )
    op.drop_index(
        op.f("ix_analytics_report_definitions_source_module"),
        table_name="analytics_report_definitions",
    )
    op.drop_index(
        op.f("ix_analytics_report_definitions_report_uuid"),
        table_name="analytics_report_definitions",
    )
    op.drop_index(
        op.f("ix_analytics_report_definitions_owner_user_id"),
        table_name="analytics_report_definitions",
    )
    op.drop_index(
        op.f("ix_analytics_report_definitions_last_generated_at"),
        table_name="analytics_report_definitions",
    )
    op.drop_index(
        op.f("ix_analytics_report_definitions_deleted_at"),
        table_name="analytics_report_definitions",
    )
    op.drop_index(
        op.f("ix_analytics_report_definitions_default_format"),
        table_name="analytics_report_definitions",
    )
    op.drop_index(
        op.f("ix_analytics_report_definitions_created_at"),
        table_name="analytics_report_definitions",
    )
    op.drop_index(
        op.f("ix_analytics_report_definitions_category"),
        table_name="analytics_report_definitions",
    )
    op.drop_table("analytics_report_definitions")

    op.drop_index(
        op.f("ix_analytics_dashboard_definitions_status"),
        table_name="analytics_dashboard_definitions",
    )
    op.drop_index(
        op.f("ix_analytics_dashboard_definitions_owner_user_id"),
        table_name="analytics_dashboard_definitions",
    )
    op.drop_index(
        op.f("ix_analytics_dashboard_definitions_deleted_at"),
        table_name="analytics_dashboard_definitions",
    )
    op.drop_index(
        op.f("ix_analytics_dashboard_definitions_dashboard_uuid"),
        table_name="analytics_dashboard_definitions",
    )
    op.drop_index(
        op.f("ix_analytics_dashboard_definitions_created_at"),
        table_name="analytics_dashboard_definitions",
    )
    op.drop_index(
        op.f("ix_analytics_dashboard_definitions_category"),
        table_name="analytics_dashboard_definitions",
    )
    op.drop_table("analytics_dashboard_definitions")
