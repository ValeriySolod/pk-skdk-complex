from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.db import get_db
from app.core.security import get_current_user
from app.models import Shipment, User
from app.schemas.shipment import ShipmentRead

router = APIRouter()

@router.get('/shipments', response_model=list[ShipmentRead])
def search_shipments(
    text: str | None = Query(default=None),
    barcode: str | None = None,
    access_mark: str | None = None,
    region: str | None = None,
    district: str | None = None,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    query = db.query(Shipment)
    if text:
        like = f'%{text}%'
        query = query.filter((Shipment.recipient_name.like(like)) | (Shipment.recipient_address.like(like)) | (Shipment.document_number.like(like)))
    if barcode:
        query = query.filter(Shipment.barcode == barcode)
    if access_mark:
        query = query.filter(Shipment.access_mark == access_mark)
    if region:
        query = query.filter(Shipment.region == region)
    if district:
        query = query.filter(Shipment.district == district)
    return query.order_by(Shipment.id.desc()).limit(200).all()
