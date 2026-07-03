"""Service layer for the organization structure module."""

from __future__ import annotations

from app.modules.organization_structure.models import (
    EmployeeAssignment,
    OrganizationUnit,
    Position,
)
from app.modules.organization_structure.repository import (
    OrganizationStructureRepository,
)
from app.modules.organization_structure.schemas import (
    EmployeeAssignmentCreate,
    EmployeeAssignmentUpdate,
    OrganizationUnitCreate,
    OrganizationUnitUpdate,
    PositionCreate,
    PositionUpdate,
)


class OrganizationStructureService:
    """Business boundary for organization structure operations."""

    def __init__(self, repository: OrganizationStructureRepository) -> None:
        self.repository = repository

    def list_units(self) -> list[OrganizationUnit]:
        return self.repository.organization_units.list()

    def get_unit(self, organization_unit_id: int) -> OrganizationUnit | None:
        return self.repository.organization_units.get_by_id(organization_unit_id)

    def create_unit(self, payload: OrganizationUnitCreate) -> OrganizationUnit:
        organization_unit = OrganizationUnit(
            name=payload.name,
            code=payload.code,
            parent_id=payload.parent_id,
            is_active=payload.is_active,
        )
        return self.repository.organization_units.create(organization_unit)

    def update_unit(
        self,
        organization_unit_id: int,
        payload: OrganizationUnitUpdate,
    ) -> OrganizationUnit | None:
        values: dict[str, object] = payload.model_dump(exclude_unset=True)
        return self.repository.organization_units.update(organization_unit_id, values)

    def delete_unit(self, organization_unit_id: int) -> bool:
        return self.repository.organization_units.delete(organization_unit_id)

    def list_positions(self) -> list[Position]:
        return self.repository.positions.list()

    def get_position(self, position_id: int) -> Position | None:
        return self.repository.positions.get_by_id(position_id)

    def create_position(self, payload: PositionCreate) -> Position:
        position = Position(
            title=payload.title,
            code=payload.code,
            organization_unit_id=payload.organization_unit_id,
            is_active=payload.is_active,
        )
        return self.repository.positions.create(position)

    def update_position(
        self,
        position_id: int,
        payload: PositionUpdate,
    ) -> Position | None:
        values: dict[str, object] = payload.model_dump(exclude_unset=True)
        return self.repository.positions.update(position_id, values)

    def delete_position(self, position_id: int) -> bool:
        return self.repository.positions.delete(position_id)

    def list_assignments(self) -> list[EmployeeAssignment]:
        return self.repository.employee_assignments.list()

    def get_assignment(self, employee_assignment_id: int) -> EmployeeAssignment | None:
        return self.repository.employee_assignments.get_by_id(employee_assignment_id)

    def create_assignment(self, payload: EmployeeAssignmentCreate) -> EmployeeAssignment:
        employee_assignment = EmployeeAssignment(
            user_id=payload.user_id,
            position_id=payload.position_id,
            start_date=payload.start_date,
            end_date=payload.end_date,
            is_active=payload.is_active,
        )
        return self.repository.employee_assignments.create(employee_assignment)

    def update_assignment(
        self,
        employee_assignment_id: int,
        payload: EmployeeAssignmentUpdate,
    ) -> EmployeeAssignment | None:
        values: dict[str, object] = payload.model_dump(exclude_unset=True)
        return self.repository.employee_assignments.update(employee_assignment_id, values)

    def delete_assignment(self, employee_assignment_id: int) -> bool:
        return self.repository.employee_assignments.delete(employee_assignment_id)
