"""Create initial application schema.

Revision ID: 20260702_0001
Revises:
Create Date: 2026-07-02 00:00:00.000000
"""

from __future__ import annotations

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa


revision: str = "20260702_0001"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "organizations",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("edrpou", sa.String(length=20), nullable=True),
        sa.Column("address", sa.Text(), nullable=False),
        sa.Column("responsible_person", sa.String(length=255), nullable=True),
        sa.Column("phone", sa.String(length=80), nullable=True),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_organizations")),
        sa.UniqueConstraint("edrpou", name=op.f("uq_organizations_edrpou")),
    )
    op.create_index(op.f("ix_organizations_name"), "organizations", ["name"], unique=False)

    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("username", sa.String(length=80), nullable=False),
        sa.Column("full_name", sa.String(length=200), nullable=False),
        sa.Column("password_hash", sa.String(length=255), nullable=False),
        sa.Column("role", sa.String(length=120), nullable=False),
        sa.Column("department", sa.String(length=160), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_users")),
    )
    op.create_index(op.f("ix_users_role"), "users", ["role"], unique=False)
    op.create_index(op.f("ix_users_username"), "users", ["username"], unique=True)

    op.create_table(
        "audit_logs",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=True),
        sa.Column("action", sa.String(length=80), nullable=False),
        sa.Column("entity_type", sa.String(length=80), nullable=False),
        sa.Column("entity_id", sa.String(length=80), nullable=False),
        sa.Column("payload", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            name=op.f("fk_audit_logs_user_id_users"),
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_audit_logs")),
    )
    op.create_index(op.f("ix_audit_logs_action"), "audit_logs", ["action"], unique=False)
    op.create_index(op.f("ix_audit_logs_created_at"), "audit_logs", ["created_at"], unique=False)
    op.create_index(op.f("ix_audit_logs_entity_id"), "audit_logs", ["entity_id"], unique=False)
    op.create_index(op.f("ix_audit_logs_entity_type"), "audit_logs", ["entity_type"], unique=False)
    op.create_index(op.f("ix_audit_logs_user_id"), "audit_logs", ["user_id"], unique=False)

    op.create_table(
        "contracts",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("organization_id", sa.Integer(), nullable=False),
        sa.Column("number", sa.String(length=100), nullable=False),
        sa.Column("signed_at", sa.Date(), nullable=False),
        sa.Column("valid_until", sa.Date(), nullable=True),
        sa.Column("confidentiality_clause", sa.Boolean(), nullable=False),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(
            ["organization_id"],
            ["organizations.id"],
            name=op.f("fk_contracts_organization_id_organizations"),
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_contracts")),
    )
    op.create_index(op.f("ix_contracts_number"), "contracts", ["number"], unique=False)
    op.create_index(op.f("ix_contracts_organization_id"), "contracts", ["organization_id"], unique=False)

    op.create_table(
        "registries",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("number", sa.String(length=120), nullable=False),
        sa.Column("sender_org_id", sa.Integer(), nullable=False),
        sa.Column("received_at", sa.DateTime(), nullable=False),
        sa.Column("qr_payload", sa.String(length=500), nullable=True),
        sa.Column("status", sa.String(length=40), nullable=False),
        sa.ForeignKeyConstraint(
            ["sender_org_id"],
            ["organizations.id"],
            name=op.f("fk_registries_sender_org_id_organizations"),
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_registries")),
    )
    op.create_index(op.f("ix_registries_number"), "registries", ["number"], unique=True)
    op.create_index(op.f("ix_registries_sender_org_id"), "registries", ["sender_org_id"], unique=False)

    op.create_table(
        "shipments",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("barcode", sa.String(length=120), nullable=False),
        sa.Column("registry_id", sa.Integer(), nullable=True),
        sa.Column("sender_org_id", sa.Integer(), nullable=True),
        sa.Column("recipient_name", sa.String(length=255), nullable=False),
        sa.Column("recipient_address", sa.Text(), nullable=False),
        sa.Column("document_number", sa.String(length=120), nullable=True),
        sa.Column("document_date", sa.String(length=40), nullable=True),
        sa.Column("weight_kg", sa.Float(), nullable=True),
        sa.Column("access_mark", sa.String(length=40), nullable=False),
        sa.Column("region", sa.String(length=120), nullable=True),
        sa.Column("district", sa.String(length=120), nullable=True),
        sa.Column("status", sa.String(length=40), nullable=False),
        sa.Column("accepted_at", sa.DateTime(), nullable=True),
        sa.Column("delivered_at", sa.DateTime(), nullable=True),
        sa.Column("current_assignee_id", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(
            ["current_assignee_id"],
            ["users.id"],
            name=op.f("fk_shipments_current_assignee_id_users"),
        ),
        sa.ForeignKeyConstraint(
            ["registry_id"],
            ["registries.id"],
            name=op.f("fk_shipments_registry_id_registries"),
        ),
        sa.ForeignKeyConstraint(
            ["sender_org_id"],
            ["organizations.id"],
            name=op.f("fk_shipments_sender_org_id_organizations"),
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_shipments")),
    )
    op.create_index(op.f("ix_shipments_barcode"), "shipments", ["barcode"], unique=True)
    op.create_index(op.f("ix_shipments_district"), "shipments", ["district"], unique=False)
    op.create_index(op.f("ix_shipments_document_number"), "shipments", ["document_number"], unique=False)
    op.create_index(op.f("ix_shipments_recipient_name"), "shipments", ["recipient_name"], unique=False)
    op.create_index(op.f("ix_shipments_region"), "shipments", ["region"], unique=False)
    op.create_index(op.f("ix_shipments_registry_id"), "shipments", ["registry_id"], unique=False)
    op.create_index(op.f("ix_shipments_status"), "shipments", ["status"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_shipments_status"), table_name="shipments")
    op.drop_index(op.f("ix_shipments_registry_id"), table_name="shipments")
    op.drop_index(op.f("ix_shipments_region"), table_name="shipments")
    op.drop_index(op.f("ix_shipments_recipient_name"), table_name="shipments")
    op.drop_index(op.f("ix_shipments_document_number"), table_name="shipments")
    op.drop_index(op.f("ix_shipments_district"), table_name="shipments")
    op.drop_index(op.f("ix_shipments_barcode"), table_name="shipments")
    op.drop_table("shipments")

    op.drop_index(op.f("ix_registries_sender_org_id"), table_name="registries")
    op.drop_index(op.f("ix_registries_number"), table_name="registries")
    op.drop_table("registries")

    op.drop_index(op.f("ix_contracts_organization_id"), table_name="contracts")
    op.drop_index(op.f("ix_contracts_number"), table_name="contracts")
    op.drop_table("contracts")

    op.drop_index(op.f("ix_audit_logs_user_id"), table_name="audit_logs")
    op.drop_index(op.f("ix_audit_logs_entity_type"), table_name="audit_logs")
    op.drop_index(op.f("ix_audit_logs_entity_id"), table_name="audit_logs")
    op.drop_index(op.f("ix_audit_logs_created_at"), table_name="audit_logs")
    op.drop_index(op.f("ix_audit_logs_action"), table_name="audit_logs")
    op.drop_table("audit_logs")

    op.drop_index(op.f("ix_users_username"), table_name="users")
    op.drop_index(op.f("ix_users_role"), table_name="users")
    op.drop_table("users")

    op.drop_index(op.f("ix_organizations_name"), table_name="organizations")
    op.drop_table("organizations")
