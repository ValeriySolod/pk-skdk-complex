from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import get_current_user, require_roles
from app.models import Shipment, Role, User
from app.schemas.shipment import ShipmentCreate, ShipmentRead, ShipmentUpdate
from app.services.audit import write_audit

router = APIRouter()

@router.get('', response_model=list[ShipmentRead])
def list_shipments(
    q: str | None = Query(default=None),
    status: str | None = None,
    region: str | None = None,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    query = db.query(Shipment)
    if q:
        like = f'%{q}%'
        query = query.filter((Shipment.barcode.like(like)) | (Shipment.recipient_name.like(like)) | (Shipment.document_number.like(like)))
    if status:
        query = query.filter(Shipment.status == status)
    if region:
        query = query.filter(Shipment.region == region)
    return query.order_by(Shipment.id.desc()).limit(100).all()

@router.post('', response_model=ShipmentRead)
def create_shipment(
    payload: ShipmentCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_roles([Role.GU_INTAKE, Role.GU_SECRET, Role.UFZ_PROCESSING, Role.SYSTEM_ADMIN, Role.NODE_ADMIN])),
):
    shipment = Shipment(**payload.model_dump())
    db.add(shipment)
    db.flush()
    write_audit(db, user, 'create', 'shipment', str(shipment.id), payload.model_dump())
    db.commit()
    db.refresh(shipment)
    return shipment

@router.patch('/{shipment_id}', response_model=ShipmentRead)
def update_shipment(
    shipment_id: int,
    payload: ShipmentUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_roles([Role.GU_INTAKE, Role.GU_SECRET, Role.GU_CONTROLLERS, Role.UFZ_PROCESSING, Role.UFZ_CONTROLLERS, Role.SYSTEM_ADMIN, Role.NODE_ADMIN])),
):
    shipment = db.get(Shipment, shipment_id)
    if not shipment:
        raise HTTPException(status_code=404, detail='Відправлення не знайдено')
    changes = payload.model_dump(exclude_unset=True)
    for key, value in changes.items():
        setattr(shipment, key, value)
    write_audit(db, user, 'update', 'shipment', str(shipment.id), changes)
    db.commit()
    db.refresh(shipment)
    return shipment
