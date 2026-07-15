from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db import get_db
from app.core.security import get_current_user
from app.models import Shipment, User
from app.schemas.shipment import ScanRequest, ShipmentRead
from app.services.audit import write_audit
from app.services.workflow import apply_delivery_timestamps, resolve_next_status

router = APIRouter()

@router.post('/barcode', response_model=ShipmentRead)
def scan_barcode(payload: ScanRequest, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    shipment = db.query(Shipment).filter(Shipment.barcode == payload.barcode).first()
    if not shipment:
        raise HTTPException(status_code=404, detail='Картку відправлення за штрих-кодом не знайдено')
    try:
        shipment.status = resolve_next_status(shipment.status, payload.next_status)
        apply_delivery_timestamps(shipment)
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    write_audit(db, user, 'scan', 'shipment', str(shipment.id), {'barcode': payload.barcode, 'status': shipment.status})
    db.commit()
    db.refresh(shipment)
    return shipment
