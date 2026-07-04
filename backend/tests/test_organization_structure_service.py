from __future__ import annotations

from datetime import date

import pytest
from sqlalchemy.orm import Session

from app.models import User
from app.modules.organization_structure.repository import OrganizationStructureRepository
from app.modules.organization_structure.schemas import (
    EmployeeAssignmentCreate,
    OrganizationUnitCreate,
    OrganizationUnitUpdate,
    PositionCreate,
)
from app.modules.organization_structure.service import OrganizationStructureService


@pytest.fixture()
def service(db_session: Session) -> OrganizationStructureService:
    return OrganizationStructureService(OrganizationStructureRepository(db_session))


def create_test_user(db_session: Session, username: str = "service-user") -> User:
    user = User(
        username=username,
        full_name="Service User",
        password_hash="not-used",
        role="test",
        is_active=True,
    )
    db_session.add(user)
    db_session.flush()
    return user


def test_create_root_and_child_organization_units(
    service: OrganizationStructureService,
) -> None:
    root_unit = service.create_unit(
        OrganizationUnitCreate(name="Head Office", code="HEAD"),
    )
    child_unit = service.create_unit(
        OrganizationUnitCreate(
            name="Operations",
            code="OPS",
            parent_id=root_unit.id,
        ),
    )

    assert root_unit.id is not None
    assert root_unit.parent_id is None
    assert child_unit.parent_id == root_unit.id
    assert child_unit.parent == root_unit
    assert root_unit.children == [child_unit]


def test_create_child_rejects_missing_parent(
    service: OrganizationStructureService,
) -> None:
    with pytest.raises(ValueError, match="Organization unit not found"):
        service.create_unit(
            OrganizationUnitCreate(
                name="Operations",
                code="OPS",
                parent_id=999,
            ),
        )


def test_create_unit_rejects_duplicate_code(
    service: OrganizationStructureService,
) -> None:
    service.create_unit(OrganizationUnitCreate(name="Head Office", code="HEAD"))

    with pytest.raises(ValueError, match="Organization unit code already exists"):
        service.create_unit(OrganizationUnitCreate(name="Head Office Copy", code="HEAD"))


def test_list_and_get_units_return_only_active_units(
    service: OrganizationStructureService,
) -> None:
    root_unit = service.create_unit(
        OrganizationUnitCreate(name="Head Office", code="HEAD"),
    )
    active_child = service.create_unit(
        OrganizationUnitCreate(name="Operations", code="OPS", parent_id=root_unit.id),
    )
    inactive_child = service.create_unit(
        OrganizationUnitCreate(
            name="Archive",
            code="ARCH",
            parent_id=root_unit.id,
            is_active=False,
        ),
    )

    units = service.list_units()

    assert [unit.code for unit in units] == ["HEAD", "OPS"]
    assert active_child.parent_id == root_unit.id
    assert service.get_unit(root_unit.id) == root_unit
    assert service.get_unit(active_child.id) == active_child
    assert service.get_unit(inactive_child.id) is None


def test_update_unit_changes_fields_and_parent(
    service: OrganizationStructureService,
) -> None:
    root_unit = service.create_unit(
        OrganizationUnitCreate(name="Head Office", code="HEAD"),
    )
    child_unit = service.create_unit(
        OrganizationUnitCreate(name="Operations", code="OPS", parent_id=root_unit.id),
    )

    updated_unit = service.update_unit(
        child_unit.id,
        OrganizationUnitUpdate(
            name="Operations Directorate",
            code="OPS-DIR",
            parent_id=None,
            is_active=False,
        ),
    )

    assert updated_unit == child_unit
    assert child_unit.name == "Operations Directorate"
    assert child_unit.code == "OPS-DIR"
    assert child_unit.parent_id is None
    assert child_unit.is_active is False


def test_update_unit_rejects_missing_parent(
    service: OrganizationStructureService,
) -> None:
    root_unit = service.create_unit(
        OrganizationUnitCreate(name="Head Office", code="HEAD"),
    )

    with pytest.raises(ValueError, match="Organization unit not found"):
        service.update_unit(
            root_unit.id,
            OrganizationUnitUpdate(parent_id=999),
        )


def test_update_unit_rejects_hierarchy_cycle(
    service: OrganizationStructureService,
) -> None:
    root_unit = service.create_unit(
        OrganizationUnitCreate(name="Head Office", code="HEAD"),
    )
    child_unit = service.create_unit(
        OrganizationUnitCreate(name="Operations", code="OPS", parent_id=root_unit.id),
    )
    grandchild_unit = service.create_unit(
        OrganizationUnitCreate(
            name="Field Team",
            code="FIELD",
            parent_id=child_unit.id,
        ),
    )

    with pytest.raises(ValueError, match="hierarchy cannot contain cycles"):
        service.update_unit(
            root_unit.id,
            OrganizationUnitUpdate(parent_id=grandchild_unit.id),
        )


def test_create_assignment_for_valid_user_and_position(
    db_session: Session,
    service: OrganizationStructureService,
) -> None:
    user = create_test_user(db_session)
    unit = service.create_unit(OrganizationUnitCreate(name="Registry", code="REG"))
    position = service.create_position(
        PositionCreate(
            title="Registrar",
            code="REG-1",
            organization_unit_id=unit.id,
        ),
    )

    assignment = service.create_assignment(
        EmployeeAssignmentCreate(
            user_id=user.id,
            position_id=position.id,
            start_date=date(2026, 1, 1),
        ),
    )

    assert assignment.user_id == user.id
    assert assignment.user == user
    assert assignment.position_id == position.id
    assert assignment.position == position
    assert assignment.position.organization_unit == unit
    assert assignment.is_active is True


def test_create_assignment_rejects_missing_position(
    db_session: Session,
    service: OrganizationStructureService,
) -> None:
    user = create_test_user(db_session)

    with pytest.raises(ValueError, match="Position not found"):
        service.create_assignment(
            EmployeeAssignmentCreate(
                user_id=user.id,
                position_id=999,
            ),
        )


def test_assignment_listing_and_get_return_only_active_assignments(
    db_session: Session,
    service: OrganizationStructureService,
) -> None:
    user = create_test_user(db_session)
    unit = service.create_unit(OrganizationUnitCreate(name="Registry", code="REG"))
    position = service.create_position(
        PositionCreate(
            title="Registrar",
            code="REG-1",
            organization_unit_id=unit.id,
        ),
    )
    active_assignment = service.create_assignment(
        EmployeeAssignmentCreate(
            user_id=user.id,
            position_id=position.id,
        ),
    )
    inactive_assignment = service.create_assignment(
        EmployeeAssignmentCreate(
            user_id=user.id,
            position_id=position.id,
            is_active=False,
        ),
    )

    assert service.list_assignments() == [active_assignment]
    assert service.get_assignment(active_assignment.id) == active_assignment
    assert service.get_assignment(inactive_assignment.id) is None
