from __future__ import annotations

from datetime import date

from sqlalchemy.orm import Session

from app.models import User
from app.modules.organization_structure.models import (
    EmployeeAssignment,
    OrganizationUnit,
    Position,
)
from app.modules.organization_structure.repository import OrganizationStructureRepository


def create_test_user(db_session: Session) -> User:
    user = User(
        username="repository-user",
        full_name="Repository User",
        password_hash="not-used",
        role="test",
        is_active=True,
    )
    db_session.add(user)
    db_session.flush()
    return user


def test_organization_unit_create_list_read_parent_update_delete(
    db_session: Session,
) -> None:
    repository = OrganizationStructureRepository(db_session)

    root_unit = repository.organization_units.create(
        OrganizationUnit(name="Head Office", code="HEAD"),
    )
    child_unit = repository.organization_units.create(
        OrganizationUnit(
            name="Operations",
            code="OPS",
            parent_id=root_unit.id,
        ),
    )

    units = repository.organization_units.list()

    assert [unit.code for unit in units] == ["HEAD", "OPS"]
    assert repository.organization_units.get_by_id(root_unit.id) == root_unit
    assert child_unit.parent_id == root_unit.id
    assert child_unit.parent == root_unit
    assert root_unit.children == [child_unit]

    updated_unit = repository.organization_units.update(
        child_unit.id,
        {"name": "Operations Directorate", "is_active": False},
    )

    assert updated_unit is child_unit
    assert child_unit.name == "Operations Directorate"
    assert child_unit.code == "OPS"
    assert child_unit.is_active is False

    assert repository.organization_units.delete(child_unit.id) is True
    assert repository.organization_units.get_by_id(child_unit.id) is None
    assert repository.organization_units.delete(child_unit.id) is False


def test_position_create_list_read_update_delete(db_session: Session) -> None:
    repository = OrganizationStructureRepository(db_session)
    unit = repository.organization_units.create(
        OrganizationUnit(name="Security", code="SEC"),
    )

    position = repository.positions.create(
        Position(
            title="Inspector",
            code="INSP",
            organization_unit_id=unit.id,
        ),
    )

    positions = repository.positions.list()

    assert positions == [position]
    assert repository.positions.get_by_id(position.id) == position
    assert position.organization_unit_id == unit.id
    assert position.organization_unit == unit
    assert unit.positions == [position]

    updated_position = repository.positions.update(
        position.id,
        {"title": "Senior Inspector", "is_active": False},
    )

    assert updated_position is position
    assert position.title == "Senior Inspector"
    assert position.code == "INSP"
    assert position.organization_unit_id == unit.id
    assert position.is_active is False

    assert repository.positions.delete(position.id) is True
    assert repository.positions.get_by_id(position.id) is None
    assert repository.positions.delete(position.id) is False


def test_employee_assignment_create_list_read_update_delete(
    db_session: Session,
) -> None:
    repository = OrganizationStructureRepository(db_session)
    user = create_test_user(db_session)
    unit = repository.organization_units.create(
        OrganizationUnit(name="Registry", code="REG"),
    )
    position = repository.positions.create(
        Position(
            title="Registrar",
            code="REG-1",
            organization_unit_id=unit.id,
        ),
    )

    assignment = repository.employee_assignments.create(
        EmployeeAssignment(
            user_id=user.id,
            position_id=position.id,
            start_date=date(2026, 1, 1),
        ),
    )

    assignments = repository.employee_assignments.list()

    assert assignments == [assignment]
    assert repository.employee_assignments.get_by_id(assignment.id) == assignment
    assert assignment.user_id == user.id
    assert assignment.user == user
    assert assignment.position_id == position.id
    assert assignment.position == position
    assert assignment.position.organization_unit == unit
    assert position.employee_assignments == [assignment]

    updated_assignment = repository.employee_assignments.update(
        assignment.id,
        {"end_date": date(2026, 12, 31), "is_active": False},
    )

    assert updated_assignment is assignment
    assert assignment.start_date == date(2026, 1, 1)
    assert assignment.end_date == date(2026, 12, 31)
    assert assignment.is_active is False

    assert repository.employee_assignments.delete(assignment.id) is True
    assert repository.employee_assignments.get_by_id(assignment.id) is None
    assert repository.employee_assignments.delete(assignment.id) is False
