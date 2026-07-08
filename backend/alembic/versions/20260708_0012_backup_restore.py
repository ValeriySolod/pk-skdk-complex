"""Create backup and restore schema.

Revision ID: 20260708_0012
Revises: 20260708_0011
Create Date: 2026-07-08 00:00:00.000000
"""

from __future__ import annotations

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision: str = "20260708_0012"
down_revision: str | None = "20260708_0011"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


json_type = postgresql.JSONB().with_variant(sa.JSON(), "sqlite")


def upgrade() -> None:
    op.create_table(
        "backup_jobs",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("job_uuid", sa.Uuid(as_uuid=True), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("backup_type", sa.String(length=40), nullable=False),
        sa.Column("status", sa.String(length=40), nullable=False),
        sa.Column("storage_location", sa.String(length=255), nullable=True),
        sa.Column("storage_path", sa.String(length=1024), nullable=True),
        sa.Column("artifact_name", sa.String(length=255), nullable=True),
        sa.Column("file_size_bytes", sa.BigInteger(), nullable=True),
        sa.Column("checksum", sa.String(length=128), nullable=True),
        sa.Column("config", json_type, nullable=True),
        sa.Column("result_summary", json_type, nullable=True),
        sa.Column("metadata", json_type, nullable=True),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("created_by_id", sa.Integer(), nullable=True),
        sa.Column("updated_by_id", sa.Integer(), nullable=True),
        sa.Column("scheduled_at", sa.DateTime(timezone=True), nullable=True),
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
            ["created_by_id"],
            ["users.id"],
            name=op.f("fk_backup_jobs_created_by_id_users"),
        ),
        sa.ForeignKeyConstraint(
            ["updated_by_id"],
            ["users.id"],
            name=op.f("fk_backup_jobs_updated_by_id_users"),
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_backup_jobs")),
    )
    for column, unique in (
        ("backup_type", False),
        ("checksum", False),
        ("completed_at", False),
        ("created_at", False),
        ("created_by_id", False),
        ("deleted_at", False),
        ("job_uuid", True),
        ("scheduled_at", False),
        ("started_at", False),
        ("status", False),
        ("storage_location", False),
        ("title", False),
        ("updated_by_id", False),
    ):
        op.create_index(
            op.f(f"ix_backup_jobs_{column}"),
            "backup_jobs",
            [column],
            unique=unique,
        )
    op.create_index(
        "ix_backup_jobs_storage_artifact",
        "backup_jobs",
        ["storage_location", "artifact_name"],
        unique=False,
    )
    op.create_index(
        "ix_backup_jobs_type_status",
        "backup_jobs",
        ["backup_type", "status"],
        unique=False,
    )

    op.create_table(
        "restore_jobs",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("job_uuid", sa.Uuid(as_uuid=True), nullable=False),
        sa.Column("backup_job_id", sa.Integer(), nullable=True),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("status", sa.String(length=40), nullable=False),
        sa.Column("restore_scope", sa.String(length=120), nullable=False),
        sa.Column("target_environment", sa.String(length=120), nullable=True),
        sa.Column("source_artifact_name", sa.String(length=255), nullable=True),
        sa.Column("source_storage_path", sa.String(length=1024), nullable=True),
        sa.Column("config", json_type, nullable=True),
        sa.Column("result_summary", json_type, nullable=True),
        sa.Column("metadata", json_type, nullable=True),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("created_by_id", sa.Integer(), nullable=True),
        sa.Column("updated_by_id", sa.Integer(), nullable=True),
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
            ["backup_job_id"],
            ["backup_jobs.id"],
            name=op.f("fk_restore_jobs_backup_job_id_backup_jobs"),
        ),
        sa.ForeignKeyConstraint(
            ["created_by_id"],
            ["users.id"],
            name=op.f("fk_restore_jobs_created_by_id_users"),
        ),
        sa.ForeignKeyConstraint(
            ["updated_by_id"],
            ["users.id"],
            name=op.f("fk_restore_jobs_updated_by_id_users"),
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_restore_jobs")),
    )
    for column, unique in (
        ("backup_job_id", False),
        ("completed_at", False),
        ("created_at", False),
        ("created_by_id", False),
        ("deleted_at", False),
        ("job_uuid", True),
        ("restore_scope", False),
        ("started_at", False),
        ("status", False),
        ("target_environment", False),
        ("title", False),
        ("updated_by_id", False),
    ):
        op.create_index(
            op.f(f"ix_restore_jobs_{column}"),
            "restore_jobs",
            [column],
            unique=unique,
        )
    op.create_index(
        "ix_restore_jobs_backup_status",
        "restore_jobs",
        ["backup_job_id", "status"],
        unique=False,
    )
    op.create_index(
        "ix_restore_jobs_scope_status",
        "restore_jobs",
        ["restore_scope", "status"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("ix_restore_jobs_scope_status", table_name="restore_jobs")
    op.drop_index("ix_restore_jobs_backup_status", table_name="restore_jobs")
    for column in (
        "updated_by_id",
        "title",
        "target_environment",
        "status",
        "started_at",
        "restore_scope",
        "job_uuid",
        "deleted_at",
        "created_by_id",
        "created_at",
        "completed_at",
        "backup_job_id",
    ):
        op.drop_index(
            op.f(f"ix_restore_jobs_{column}"),
            table_name="restore_jobs",
        )
    op.drop_table("restore_jobs")

    op.drop_index("ix_backup_jobs_type_status", table_name="backup_jobs")
    op.drop_index("ix_backup_jobs_storage_artifact", table_name="backup_jobs")
    for column in (
        "updated_by_id",
        "title",
        "storage_location",
        "status",
        "started_at",
        "scheduled_at",
        "job_uuid",
        "deleted_at",
        "created_by_id",
        "created_at",
        "completed_at",
        "checksum",
        "backup_type",
    ):
        op.drop_index(
            op.f(f"ix_backup_jobs_{column}"),
            table_name="backup_jobs",
        )
    op.drop_table("backup_jobs")
