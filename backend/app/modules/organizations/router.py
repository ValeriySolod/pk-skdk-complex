from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user, require_roles
from app.models import Organization, Role, User
from app.schemas.organization import (
    OrganizationCreate,
    OrganizationRead,
    OrganizationUpdate,
)
from app.services.audit import write_audit

router = APIRouter()


@router.get("", response_model=list[OrganizationRead])
def list_organizations(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return db.query(Organization).order_by(Organization.name).all()


@router.get("/{organization_id}", response_model=OrganizationRead)
def get_organization(
    organization_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    org = db.get(Organization, organization_id)

    if not org:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Організацію не знайдено",
        )

    return org


@router.post("", response_model=OrganizationRead, status_code=status.HTTP_201_CREATED)
def create_organization(
    payload: OrganizationCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_roles([Role.SYSTEM_ADMIN, Role.NODE_ADMIN])),
):
    if payload.edrpou:
        existing = (
            db.query(Organization).filter(Organization.edrpou == payload.edrpou).first()
        )

        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Організація з таким ЄДРПОУ вже існує",
            )

    org = Organization(**payload.model_dump())

    db.add(org)
    db.flush()

    write_audit(db, user, "create", "organization", str(org.id), payload.model_dump())

    db.commit()
    db.refresh(org)

    return org


@router.put("/{organization_id}", response_model=OrganizationRead)
def update_organization(
    organization_id: int,
    payload: OrganizationUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_roles([Role.SYSTEM_ADMIN, Role.NODE_ADMIN])),
):
    org = db.get(Organization, organization_id)

    if not org:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Організацію не знайдено",
        )

    update_data = payload.model_dump(exclude_unset=True)

    if "edrpou" in update_data and update_data["edrpou"]:
        existing = (
            db.query(Organization)
            .filter(
                Organization.edrpou == update_data["edrpou"],
                Organization.id != organization_id,
            )
            .first()
        )

        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Організація з таким ЄДРПОУ вже існує",
            )

    for field, value in update_data.items():
        setattr(org, field, value)

    write_audit(db, user, "update", "organization", str(org.id), update_data)

    db.commit()
    db.refresh(org)

    return org


@router.delete("/{organization_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_organization(
    organization_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_roles([Role.SYSTEM_ADMIN])),
):
    org = db.get(Organization, organization_id)

    if not org:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Організацію не знайдено",
        )

    write_audit(db, user, "delete", "organization", str(org.id), {"name": org.name})

    db.delete(org)
    db.commit()

    return None
