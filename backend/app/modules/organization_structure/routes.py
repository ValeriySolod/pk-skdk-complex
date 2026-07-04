from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.dependencies import get_db
from app.core.security import get_current_user
from app.models import User
from app.modules.organization_structure.repository import OrganizationStructureRepository
from app.modules.organization_structure.schemas import (
    EmployeeAssignmentCreate,
    EmployeeAssignmentRead,
    EmployeeAssignmentUpdate,
    OrganizationUnitCreate,
    OrganizationUnitRead,
    OrganizationUnitUpdate,
    PositionCreate,
    PositionRead,
    PositionUpdate,
)
from app.modules.organization_structure.service import OrganizationStructureService


router = APIRouter()


def get_organization_structure_service(
    db: Session = Depends(get_db),
) -> OrganizationStructureService:
    repository = OrganizationStructureRepository(db)
    return OrganizationStructureService(repository)


@router.get("/health")
def module_health(_: User = Depends(get_current_user)):
    return {"status": "ok"}


@router.get("/units", response_model=list[OrganizationUnitRead])
def list_units(
    service: OrganizationStructureService = Depends(get_organization_structure_service),
    _: User = Depends(get_current_user),
):
    return service.list_units()


@router.post(
    "/units",
    response_model=OrganizationUnitRead,
    status_code=status.HTTP_201_CREATED,
)
def create_unit(
    payload: OrganizationUnitCreate,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    service = get_organization_structure_service(db)
    organization_unit = service.create_unit(payload)
    db.commit()
    db.refresh(organization_unit)
    return organization_unit


@router.get("/units/{unit_id}", response_model=OrganizationUnitRead)
def get_unit(
    unit_id: int,
    service: OrganizationStructureService = Depends(get_organization_structure_service),
    _: User = Depends(get_current_user),
):
    organization_unit = service.get_unit(unit_id)
    if organization_unit is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organization unit not found",
        )
    return organization_unit


@router.patch("/units/{unit_id}", response_model=OrganizationUnitRead)
def update_unit(
    unit_id: int,
    payload: OrganizationUnitUpdate,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    service = get_organization_structure_service(db)
    organization_unit = service.update_unit(unit_id, payload)
    if organization_unit is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organization unit not found",
        )
    db.commit()
    db.refresh(organization_unit)
    return organization_unit


@router.get("/positions", response_model=list[PositionRead])
def list_positions(
    service: OrganizationStructureService = Depends(get_organization_structure_service),
    _: User = Depends(get_current_user),
):
    return service.list_positions()


@router.post(
    "/positions",
    response_model=PositionRead,
    status_code=status.HTTP_201_CREATED,
)
def create_position(
    payload: PositionCreate,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    service = get_organization_structure_service(db)
    position = service.create_position(payload)
    db.commit()
    db.refresh(position)
    return position


@router.get("/positions/{position_id}", response_model=PositionRead)
def get_position(
    position_id: int,
    service: OrganizationStructureService = Depends(get_organization_structure_service),
    _: User = Depends(get_current_user),
):
    position = service.get_position(position_id)
    if position is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Position not found",
        )
    return position


@router.patch("/positions/{position_id}", response_model=PositionRead)
def update_position(
    position_id: int,
    payload: PositionUpdate,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    service = get_organization_structure_service(db)
    position = service.update_position(position_id, payload)
    if position is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Position not found",
        )
    db.commit()
    db.refresh(position)
    return position


@router.get("/assignments", response_model=list[EmployeeAssignmentRead])
def list_assignments(
    service: OrganizationStructureService = Depends(get_organization_structure_service),
    _: User = Depends(get_current_user),
):
    return service.list_assignments()


@router.post(
    "/assignments",
    response_model=EmployeeAssignmentRead,
    status_code=status.HTTP_201_CREATED,
)
def create_assignment(
    payload: EmployeeAssignmentCreate,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    service = get_organization_structure_service(db)
    assignment = service.create_assignment(payload)
    db.commit()
    db.refresh(assignment)
    return assignment


@router.get("/assignments/{assignment_id}", response_model=EmployeeAssignmentRead)
def get_assignment(
    assignment_id: int,
    service: OrganizationStructureService = Depends(get_organization_structure_service),
    _: User = Depends(get_current_user),
):
    assignment = service.get_assignment(assignment_id)
    if assignment is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Employee assignment not found",
        )
    return assignment


@router.patch("/assignments/{assignment_id}", response_model=EmployeeAssignmentRead)
def update_assignment(
    assignment_id: int,
    payload: EmployeeAssignmentUpdate,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    service = get_organization_structure_service(db)
    assignment = service.update_assignment(assignment_id, payload)
    if assignment is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Employee assignment not found",
        )
    db.commit()
    db.refresh(assignment)
    return assignment
