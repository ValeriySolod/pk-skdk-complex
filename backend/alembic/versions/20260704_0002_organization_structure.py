"""Create organization structure schema.

Revision ID: 20260704_0002
Revises: 20260702_0001
Create Date: 2026-07-04 00:00:00.000000
"""

from __future__ import annotations

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa


revision: str = "20260704_0002"
down_revision: str | None = "20260702_0001"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "organization_units",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("code", sa.String(length=80), nullable=True),
        sa.Column("parent_id", sa.Integer(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.ForeignKeyConstraint(
            ["parent_id"],
            ["organization_units.id"],
            name=op.f("fk_organization_units_parent_id_organization_units"),
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_organization_units")),
    )
    op.create_index(
        op.f("ix_organization_units_code"),
        "organization_units",
        ["code"],
        unique=True,
    )
    op.create_index(
        op.f("ix_organization_units_name"),
        "organization_units",
        ["name"],
        unique=False,
    )
    op.create_index(
        op.f("ix_organization_units_parent_id"),
        "organization_units",
        ["parent_id"],
        unique=False,
    )

    op.create_table(
        "positions",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("organization_unit_id", sa.Integer(), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("code", sa.String(length=80), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.ForeignKeyConstraint(
            ["organization_unit_id"],
            ["organization_units.id"],
            name=op.f("fk_positions_organization_unit_id_organization_units"),
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_positions")),
    )
    op.create_index(op.f("ix_positions_code"), "positions", ["code"], unique=True)
    op.create_index(
        op.f("ix_positions_organization_unit_id"),
        "positions",
        ["organization_unit_id"],
        unique=False,
    )
    op.create_index(op.f("ix_positions_title"), "positions", ["title"], unique=False)

    op.create_table(
        "employee_assignments",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("position_id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("start_date", sa.Date(), nullable=True),
        sa.Column("end_date", sa.Date(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.ForeignKeyConstraint(
            ["position_id"],
            ["positions.id"],
            name=op.f("fk_employee_assignments_position_id_positions"),
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            name=op.f("fk_employee_assignments_user_id_users"),
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_employee_assignments")),
    )
    op.create_index(
        op.f("ix_employee_assignments_position_id"),
        "employee_assignments",
        ["position_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_employee_assignments_user_id"),
        "employee_assignments",
        ["user_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(
        op.f("ix_employee_assignments_user_id"),
        table_name="employee_assignments",
    )
    op.drop_index(
        op.f("ix_employee_assignments_position_id"),
        table_name="employee_assignments",
    )
    op.drop_table("employee_assignments")

    op.drop_index(op.f("ix_positions_title"), table_name="positions")
    op.drop_index(
        op.f("ix_positions_organization_unit_id"),
        table_name="positions",
    )
    op.drop_index(op.f("ix_positions_code"), table_name="positions")
    op.drop_table("positions")

    op.drop_index(
        op.f("ix_organization_units_parent_id"),
        table_name="organization_units",
    )
    op.drop_index(
        op.f("ix_organization_units_name"),
        table_name="organization_units",
    )
    op.drop_index(
        op.f("ix_organization_units_code"),
        table_name="organization_units",
    )
    op.drop_table("organization_units")
