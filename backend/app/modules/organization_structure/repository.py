"""Repository skeletons for the organization structure module."""

from __future__ import annotations

from collections.abc import Mapping

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.modules.organization_structure.models import (
    EmployeeAssignment,
    OrganizationUnit,
    Position,
)


class OrganizationUnitRepository:
    """Persistence operations for organization units."""

    def __init__(self, db: Session) -> None:
        self.db = db

    def get_by_id(self, organization_unit_id: int) -> OrganizationUnit | None:
        return self.db.get(OrganizationUnit, organization_unit_id)

    def list(self) -> list[OrganizationUnit]:
        return list(self.db.scalars(select(OrganizationUnit)).all())

    def create(self, organization_unit: OrganizationUnit) -> OrganizationUnit:
        self.db.add(organization_unit)
        self.db.flush()
        return organization_unit

    def update(
        self,
        organization_unit_id: int,
        values: Mapping[str, object],
    ) -> OrganizationUnit | None:
        organization_unit = self.get_by_id(organization_unit_id)
        if organization_unit is None:
            return None

        for field, value in values.items():
            setattr(organization_unit, field, value)

        self.db.flush()
        return organization_unit

    def delete(self, organization_unit_id: int) -> bool:
        organization_unit = self.get_by_id(organization_unit_id)
        if organization_unit is None:
            return False

        self.db.delete(organization_unit)
        self.db.flush()
        return True


class PositionRepository:
    """Persistence operations for positions."""

    def __init__(self, db: Session) -> None:
        self.db = db

    def get_by_id(self, position_id: int) -> Position | None:
        return self.db.get(Position, position_id)

    def list(self) -> list[Position]:
        return list(self.db.scalars(select(Position)).all())

    def create(self, position: Position) -> Position:
        self.db.add(position)
        self.db.flush()
        return position

    def update(
        self,
        position_id: int,
        values: Mapping[str, object],
    ) -> Position | None:
        position = self.get_by_id(position_id)
        if position is None:
            return None

        for field, value in values.items():
            setattr(position, field, value)

        self.db.flush()
        return position

    def delete(self, position_id: int) -> bool:
        position = self.get_by_id(position_id)
        if position is None:
            return False

        self.db.delete(position)
        self.db.flush()
        return True


class EmployeeAssignmentRepository:
    """Persistence operations for employee assignments."""

    def __init__(self, db: Session) -> None:
        self.db = db

    def get_by_id(self, employee_assignment_id: int) -> EmployeeAssignment | None:
        return self.db.get(EmployeeAssignment, employee_assignment_id)

    def list(self) -> list[EmployeeAssignment]:
        return list(self.db.scalars(select(EmployeeAssignment)).all())

    def create(self, employee_assignment: EmployeeAssignment) -> EmployeeAssignment:
        self.db.add(employee_assignment)
        self.db.flush()
        return employee_assignment

    def update(
        self,
        employee_assignment_id: int,
        values: Mapping[str, object],
    ) -> EmployeeAssignment | None:
        employee_assignment = self.get_by_id(employee_assignment_id)
        if employee_assignment is None:
            return None

        for field, value in values.items():
            setattr(employee_assignment, field, value)

        self.db.flush()
        return employee_assignment

    def delete(self, employee_assignment_id: int) -> bool:
        employee_assignment = self.get_by_id(employee_assignment_id)
        if employee_assignment is None:
            return False

        self.db.delete(employee_assignment)
        self.db.flush()
        return True


class OrganizationStructureRepository:
    """Aggregate access point for organization structure repositories."""

    def __init__(self, db: Session) -> None:
        self.db = db
        self.organization_units = OrganizationUnitRepository(db)
        self.positions = PositionRepository(db)
        self.employee_assignments = EmployeeAssignmentRepository(db)


__all__ = [
    "EmployeeAssignmentRepository",
    "OrganizationStructureRepository",
    "OrganizationUnitRepository",
    "PositionRepository",
]
