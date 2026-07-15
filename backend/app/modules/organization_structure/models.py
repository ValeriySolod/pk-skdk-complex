from __future__ import annotations

from datetime import date
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, Date, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base

if TYPE_CHECKING:
    from app.models import User


class OrganizationUnit(Base):
    __tablename__ = "organization_units"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255), index=True)
    code: Mapped[str | None] = mapped_column(String(80), unique=True, index=True, nullable=True)
    parent_id: Mapped[int | None] = mapped_column(
        ForeignKey("organization_units.id"),
        nullable=True,
        index=True,
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    parent: Mapped[OrganizationUnit | None] = relationship(
        "OrganizationUnit",
        remote_side=lambda: OrganizationUnit.id,
        back_populates="children",
    )
    children: Mapped[list[OrganizationUnit]] = relationship(
        "OrganizationUnit",
        back_populates="parent",
    )
    positions: Mapped[list[Position]] = relationship(back_populates="organization_unit")


class Position(Base):
    __tablename__ = "positions"

    id: Mapped[int] = mapped_column(primary_key=True)
    organization_unit_id: Mapped[int] = mapped_column(
        ForeignKey("organization_units.id"),
        nullable=False,
        index=True,
    )
    title: Mapped[str] = mapped_column(String(255), index=True)
    code: Mapped[str | None] = mapped_column(String(80), unique=True, index=True, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    organization_unit: Mapped[OrganizationUnit] = relationship(back_populates="positions")
    employee_assignments: Mapped[list[EmployeeAssignment]] = relationship(
        back_populates="position",
    )


class EmployeeAssignment(Base):
    __tablename__ = "employee_assignments"

    id: Mapped[int] = mapped_column(primary_key=True)
    position_id: Mapped[int] = mapped_column(
        ForeignKey("positions.id"),
        nullable=False,
        index=True,
    )
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    start_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    end_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    position: Mapped[Position] = relationship(back_populates="employee_assignments")
    user: Mapped[User] = relationship("User")
