"""Create file storage schema.

Revision ID: 20260705_0006
Revises: 20260705_0005
Create Date: 2026-07-05 00:00:00.000000
"""

from __future__ import annotations

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision: str = "20260705_0006"
down_revision: str | None = "20260705_0005"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "file_storage_objects",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("uuid", sa.Uuid(as_uuid=True), nullable=False),
        sa.Column("original_filename", sa.String(length=255), nullable=False),
        sa.Column("storage_key", sa.String(length=1024), nullable=False),
        sa.Column("content_type", sa.String(length=255), nullable=True),
        sa.Column("extension", sa.String(length=32), nullable=True),
        sa.Column("size_bytes", sa.BigInteger(), nullable=False),
        sa.Column("checksum_sha256", sa.String(length=64), nullable=True),
        sa.Column("storage_provider", sa.String(length=40), nullable=False),
        sa.Column("storage_bucket", sa.String(length=255), nullable=True),
        sa.Column("storage_path", sa.String(length=1024), nullable=False),
        sa.Column("status", sa.String(length=40), nullable=False),
        sa.Column("access_scope", sa.String(length=40), nullable=False),
        sa.Column("owner_user_id", sa.Integer(), nullable=True),
        sa.Column("related_entity_type", sa.String(length=120), nullable=True),
        sa.Column("related_entity_id", sa.String(length=120), nullable=True),
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
        sa.ForeignKeyConstraint(
            ["owner_user_id"],
            ["users.id"],
            name=op.f("fk_file_storage_objects_owner_user_id_users"),
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_file_storage_objects")),
        sa.UniqueConstraint(
            "storage_key",
            name=op.f("uq_file_storage_objects_storage_key"),
        ),
    )
    op.create_index(
        op.f("ix_file_storage_objects_access_scope"),
        "file_storage_objects",
        ["access_scope"],
        unique=False,
    )
    op.create_index(
        op.f("ix_file_storage_objects_checksum_sha256"),
        "file_storage_objects",
        ["checksum_sha256"],
        unique=False,
    )
    op.create_index(
        op.f("ix_file_storage_objects_created_at"),
        "file_storage_objects",
        ["created_at"],
        unique=False,
    )
    op.create_index(
        op.f("ix_file_storage_objects_deleted_at"),
        "file_storage_objects",
        ["deleted_at"],
        unique=False,
    )
    op.create_index(
        op.f("ix_file_storage_objects_owner_user_id"),
        "file_storage_objects",
        ["owner_user_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_file_storage_objects_related_entity_id"),
        "file_storage_objects",
        ["related_entity_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_file_storage_objects_related_entity_type"),
        "file_storage_objects",
        ["related_entity_type"],
        unique=False,
    )
    op.create_index(
        op.f("ix_file_storage_objects_status"),
        "file_storage_objects",
        ["status"],
        unique=False,
    )
    op.create_index(
        op.f("ix_file_storage_objects_uuid"),
        "file_storage_objects",
        ["uuid"],
        unique=True,
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_file_storage_objects_uuid"), table_name="file_storage_objects")
    op.drop_index(
        op.f("ix_file_storage_objects_status"),
        table_name="file_storage_objects",
    )
    op.drop_index(
        op.f("ix_file_storage_objects_related_entity_type"),
        table_name="file_storage_objects",
    )
    op.drop_index(
        op.f("ix_file_storage_objects_related_entity_id"),
        table_name="file_storage_objects",
    )
    op.drop_index(
        op.f("ix_file_storage_objects_owner_user_id"),
        table_name="file_storage_objects",
    )
    op.drop_index(
        op.f("ix_file_storage_objects_deleted_at"),
        table_name="file_storage_objects",
    )
    op.drop_index(
        op.f("ix_file_storage_objects_created_at"),
        table_name="file_storage_objects",
    )
    op.drop_index(
        op.f("ix_file_storage_objects_checksum_sha256"),
        table_name="file_storage_objects",
    )
    op.drop_index(
        op.f("ix_file_storage_objects_access_scope"),
        table_name="file_storage_objects",
    )
    op.drop_table("file_storage_objects")
