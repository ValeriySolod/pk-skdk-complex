"""Create document management schema.

Revision ID: 20260705_0004
Revises: 20260704_0003
Create Date: 2026-07-05 00:00:00.000000
"""

from __future__ import annotations

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision: str = "20260705_0004"
down_revision: str | None = "20260704_0003"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "documents",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("document_number", sa.String(length=120), nullable=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("document_type", sa.String(length=120), nullable=False),
        sa.Column("status", sa.String(length=80), nullable=False),
        sa.Column("organization_id", sa.Integer(), nullable=True),
        sa.Column("owner_user_id", sa.Integer(), nullable=True),
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
            ["organization_id"],
            ["organization_units.id"],
            name=op.f("fk_documents_organization_id_organization_units"),
        ),
        sa.ForeignKeyConstraint(
            ["owner_user_id"],
            ["users.id"],
            name=op.f("fk_documents_owner_user_id_users"),
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_documents")),
        sa.UniqueConstraint(
            "document_number",
            name=op.f("uq_documents_document_number"),
        ),
    )
    op.create_index(
        op.f("ix_documents_document_number"),
        "documents",
        ["document_number"],
        unique=False,
    )
    op.create_index(
        op.f("ix_documents_document_type"),
        "documents",
        ["document_type"],
        unique=False,
    )
    op.create_index(
        op.f("ix_documents_organization_id"),
        "documents",
        ["organization_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_documents_owner_user_id"),
        "documents",
        ["owner_user_id"],
        unique=False,
    )
    op.create_index(op.f("ix_documents_status"), "documents", ["status"], unique=False)
    op.create_index(op.f("ix_documents_title"), "documents", ["title"], unique=False)

    op.create_table(
        "document_categories",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("code", sa.String(length=80), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_document_categories")),
        sa.UniqueConstraint("code", name=op.f("uq_document_categories_code")),
    )
    op.create_index(
        op.f("ix_document_categories_code"),
        "document_categories",
        ["code"],
        unique=False,
    )
    op.create_index(
        op.f("ix_document_categories_is_active"),
        "document_categories",
        ["is_active"],
        unique=False,
    )
    op.create_index(
        op.f("ix_document_categories_name"),
        "document_categories",
        ["name"],
        unique=False,
    )

    op.create_table(
        "document_tags",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("color", sa.String(length=40), nullable=True),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_document_tags")),
        sa.UniqueConstraint("name", name=op.f("uq_document_tags_name")),
    )
    op.create_index(
        op.f("ix_document_tags_name"),
        "document_tags",
        ["name"],
        unique=False,
    )

    op.create_table(
        "document_versions",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("document_id", sa.Integer(), nullable=False),
        sa.Column("version", sa.String(length=80), nullable=False),
        sa.Column("file_name", sa.String(length=255), nullable=False),
        sa.Column("storage_path", sa.String(length=1024), nullable=False),
        sa.Column("checksum", sa.String(length=255), nullable=True),
        sa.Column("uploaded_by", sa.Integer(), nullable=True),
        sa.Column(
            "uploaded_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["document_id"],
            ["documents.id"],
            name=op.f("fk_document_versions_document_id_documents"),
        ),
        sa.ForeignKeyConstraint(
            ["uploaded_by"],
            ["users.id"],
            name=op.f("fk_document_versions_uploaded_by_users"),
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_document_versions")),
    )
    op.create_index(
        op.f("ix_document_versions_document_id"),
        "document_versions",
        ["document_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_document_versions_uploaded_at"),
        "document_versions",
        ["uploaded_at"],
        unique=False,
    )
    op.create_index(
        op.f("ix_document_versions_uploaded_by"),
        "document_versions",
        ["uploaded_by"],
        unique=False,
    )
    op.create_index(
        op.f("ix_document_versions_version"),
        "document_versions",
        ["version"],
        unique=False,
    )

    op.create_table(
        "document_tag_assignments",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("document_id", sa.Integer(), nullable=False),
        sa.Column("tag_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["document_id"],
            ["documents.id"],
            name=op.f("fk_document_tag_assignments_document_id_documents"),
        ),
        sa.ForeignKeyConstraint(
            ["tag_id"],
            ["document_tags.id"],
            name=op.f("fk_document_tag_assignments_tag_id_document_tags"),
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_document_tag_assignments")),
        sa.UniqueConstraint(
            "document_id",
            "tag_id",
            name="uq_document_tag_assignment_document_tag",
        ),
    )
    op.create_index(
        op.f("ix_document_tag_assignments_document_id"),
        "document_tag_assignments",
        ["document_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_document_tag_assignments_tag_id"),
        "document_tag_assignments",
        ["tag_id"],
        unique=False,
    )

    op.create_table(
        "document_permissions",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("document_id", sa.Integer(), nullable=False),
        sa.Column("principal_type", sa.String(length=80), nullable=False),
        sa.Column("principal_id", sa.Integer(), nullable=False),
        sa.Column("permission", sa.String(length=80), nullable=False),
        sa.ForeignKeyConstraint(
            ["document_id"],
            ["documents.id"],
            name=op.f("fk_document_permissions_document_id_documents"),
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_document_permissions")),
        sa.UniqueConstraint(
            "document_id",
            "principal_type",
            "principal_id",
            "permission",
            name="uq_document_permission_principal",
        ),
    )
    op.create_index(
        op.f("ix_document_permissions_document_id"),
        "document_permissions",
        ["document_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_document_permissions_permission"),
        "document_permissions",
        ["permission"],
        unique=False,
    )
    op.create_index(
        op.f("ix_document_permissions_principal_id"),
        "document_permissions",
        ["principal_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_document_permissions_principal_type"),
        "document_permissions",
        ["principal_type"],
        unique=False,
    )

    op.create_table(
        "document_audit_events",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("document_id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=True),
        sa.Column("action", sa.String(length=120), nullable=False),
        sa.Column(
            "metadata_json",
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
            ["document_id"],
            ["documents.id"],
            name=op.f("fk_document_audit_events_document_id_documents"),
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            name=op.f("fk_document_audit_events_user_id_users"),
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_document_audit_events")),
    )
    op.create_index(
        op.f("ix_document_audit_events_action"),
        "document_audit_events",
        ["action"],
        unique=False,
    )
    op.create_index(
        op.f("ix_document_audit_events_created_at"),
        "document_audit_events",
        ["created_at"],
        unique=False,
    )
    op.create_index(
        op.f("ix_document_audit_events_document_id"),
        "document_audit_events",
        ["document_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_document_audit_events_user_id"),
        "document_audit_events",
        ["user_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(
        op.f("ix_document_audit_events_user_id"),
        table_name="document_audit_events",
    )
    op.drop_index(
        op.f("ix_document_audit_events_document_id"),
        table_name="document_audit_events",
    )
    op.drop_index(
        op.f("ix_document_audit_events_created_at"),
        table_name="document_audit_events",
    )
    op.drop_index(
        op.f("ix_document_audit_events_action"),
        table_name="document_audit_events",
    )
    op.drop_table("document_audit_events")

    op.drop_index(
        op.f("ix_document_permissions_principal_type"),
        table_name="document_permissions",
    )
    op.drop_index(
        op.f("ix_document_permissions_principal_id"),
        table_name="document_permissions",
    )
    op.drop_index(
        op.f("ix_document_permissions_permission"),
        table_name="document_permissions",
    )
    op.drop_index(
        op.f("ix_document_permissions_document_id"),
        table_name="document_permissions",
    )
    op.drop_table("document_permissions")

    op.drop_index(
        op.f("ix_document_tag_assignments_tag_id"),
        table_name="document_tag_assignments",
    )
    op.drop_index(
        op.f("ix_document_tag_assignments_document_id"),
        table_name="document_tag_assignments",
    )
    op.drop_table("document_tag_assignments")

    op.drop_index(
        op.f("ix_document_versions_version"),
        table_name="document_versions",
    )
    op.drop_index(
        op.f("ix_document_versions_uploaded_by"),
        table_name="document_versions",
    )
    op.drop_index(
        op.f("ix_document_versions_uploaded_at"),
        table_name="document_versions",
    )
    op.drop_index(
        op.f("ix_document_versions_document_id"),
        table_name="document_versions",
    )
    op.drop_table("document_versions")

    op.drop_index(op.f("ix_document_tags_name"), table_name="document_tags")
    op.drop_table("document_tags")

    op.drop_index(
        op.f("ix_document_categories_name"),
        table_name="document_categories",
    )
    op.drop_index(
        op.f("ix_document_categories_is_active"),
        table_name="document_categories",
    )
    op.drop_index(
        op.f("ix_document_categories_code"),
        table_name="document_categories",
    )
    op.drop_table("document_categories")

    op.drop_index(op.f("ix_documents_title"), table_name="documents")
    op.drop_index(op.f("ix_documents_status"), table_name="documents")
    op.drop_index(op.f("ix_documents_owner_user_id"), table_name="documents")
    op.drop_index(op.f("ix_documents_organization_id"), table_name="documents")
    op.drop_index(op.f("ix_documents_document_type"), table_name="documents")
    op.drop_index(op.f("ix_documents_document_number"), table_name="documents")
    op.drop_table("documents")
