from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import require_roles, get_current_user
from app.models import Registry, Role, User
from app.schemas.registry import RegistryCreate, RegistryRead
from app.services.audit import write_audit

router = APIRouter()

@router.get('', response_model=list[RegistryRead])
def list_registries(db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    return db.query(Registry).order_by(Registry.received_at.desc()).limit(100).all()

@router.post('', response_model=RegistryRead)
def create_registry(
    payload: RegistryCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_roles([Role.GU_INTAKE, Role.GU_SECRET, Role.SYSTEM_ADMIN, Role.NODE_ADMIN])),
):
    registry = Registry(**payload.model_dump())
    db.add(registry)
    db.flush()
    write_audit(db, user, 'create', 'registry', str(registry.id), payload.model_dump())
    db.commit()
    db.refresh(registry)
    return registry

@router.get('/{registry_id}', response_model=RegistryRead)
def get_registry(registry_id: int, db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    registry = db.get(Registry, registry_id)
    if not registry:
        raise HTTPException(status_code=404, detail='Реєстр не знайдено')
    return registry
