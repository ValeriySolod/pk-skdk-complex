from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import get_current_user, require_roles
from app.models import Organization, Role, User
from app.schemas.organization import OrganizationCreate, OrganizationRead
from app.services.audit import write_audit

router = APIRouter()

@router.get('', response_model=list[OrganizationRead])
def list_organizations(db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    return db.query(Organization).order_by(Organization.name).limit(100).all()

@router.post('', response_model=OrganizationRead)
def create_organization(
    payload: OrganizationCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_roles([Role.SYSTEM_ADMIN, Role.NODE_ADMIN, Role.GU_INTAKE])),
):
    org = Organization(**payload.model_dump())
    db.add(org)
    db.flush()
    write_audit(db, user, 'create', 'organization', str(org.id), payload.model_dump())
    db.commit()
    db.refresh(org)
    return org

@router.get('/{organization_id}', response_model=OrganizationRead)
def get_organization(organization_id: int, db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    org = db.get(Organization, organization_id)
    if not org:
        raise HTTPException(status_code=404, detail='Організацію не знайдено')
    return org
