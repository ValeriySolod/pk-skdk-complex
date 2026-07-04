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
        return self.repository.organization_units.list_active()

    def get_unit(self, organization_unit_id: int) -> OrganizationUnit | None:
        return self.repository.organization_units.get_active_by_id(organization_unit_id)

    def create_unit(self, payload: OrganizationUnitCreate) -> OrganizationUnit:
        self._validate_unit_parent(payload.parent_id)
        self._validate_unique_unit_code(payload.code)

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

        if "parent_id" in values:
            parent_id = values["parent_id"]
            if not isinstance(parent_id, int | None):
                raise ValueError("Invalid parent organization unit")
            self._validate_unit_parent(parent_id, organization_unit_id)

        if "code" in values:
            code = values["code"]
            if not isinstance(code, str | None):
                raise ValueError("Invalid organization unit code")
            self._validate_unique_unit_code(code, organization_unit_id)

        return self.repository.organization_units.update(organization_unit_id, values)

    def delete_unit(self, organization_unit_id: int) -> bool:
        return self.repository.organization_units.delete(organization_unit_id)

    def list_positions(self) -> list[Position]:
        return self.repository.positions.list_active()

    def get_position(self, position_id: int) -> Position | None:
        return self.repository.positions.get_active_by_id(position_id)

    def create_position(self, payload: PositionCreate) -> Position:
        self._require_active_unit(payload.organization_unit_id)

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

        if "organization_unit_id" in values:
            organization_unit_id = values["organization_unit_id"]
            if not isinstance(organization_unit_id, int):
                raise ValueError("Invalid organization unit")
            self._require_active_unit(organization_unit_id)

        return self.repository.positions.update(position_id, values)

    def delete_position(self, position_id: int) -> bool:
        return self.repository.positions.delete(position_id)

    def list_assignments(self) -> list[EmployeeAssignment]:
        return self.repository.employee_assignments.list_active()

    def get_assignment(self, employee_assignment_id: int) -> EmployeeAssignment | None:
        return self.repository.employee_assignments.get_active_by_id(employee_assignment_id)

    def create_assignment(self, payload: EmployeeAssignmentCreate) -> EmployeeAssignment:
        self._require_active_position(payload.position_id)

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

        if "position_id" in values:
            position_id = values["position_id"]
            if not isinstance(position_id, int):
                raise ValueError("Invalid position")
            self._require_active_position(position_id)

        return self.repository.employee_assignments.update(employee_assignment_id, values)

    def delete_assignment(self, employee_assignment_id: int) -> bool:
        return self.repository.employee_assignments.delete(employee_assignment_id)

    def _validate_unit_parent(
        self,
        parent_id: int | None,
        organization_unit_id: int | None = None,
    ) -> None:
        if parent_id is None:
            return

        if organization_unit_id is not None and parent_id == organization_unit_id:
            raise ValueError("Organization unit cannot be its own parent")

        parent = self._require_active_unit(parent_id)
        while parent.parent_id is not None:
            if parent.parent_id == organization_unit_id:
                raise ValueError("Organization unit hierarchy cannot contain cycles")
            parent = self._require_active_unit(parent.parent_id)

    def _validate_unique_unit_code(
        self,
        code: str | None,
        organization_unit_id: int | None = None,
    ) -> None:
        if code is None:
            return

        existing_unit = self.repository.organization_units.get_by_code(code)
        if existing_unit is not None and existing_unit.id != organization_unit_id:
            raise ValueError("Organization unit code already exists")

    def _require_active_unit(self, organization_unit_id: int) -> OrganizationUnit:
        organization_unit = self.repository.organization_units.get_active_by_id(
            organization_unit_id,
        )
        if organization_unit is None:
            raise ValueError("Organization unit not found")
        return organization_unit

    def _require_active_position(self, position_id: int) -> Position:
        position = self.repository.positions.get_active_by_id(position_id)
        if position is None:
            raise ValueError("Position not found")
        return position
