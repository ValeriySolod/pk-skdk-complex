from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session
from app.db import get_db
from app.core.security import get_current_user
from app.models import Organization, Shipment, User

router = APIRouter()

@router.get('/shipments-by-organization')
def shipments_by_organization(db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    rows = (
        db.query(Organization.name, func.count(Shipment.id).label('shipments_count'))
        .join(Shipment, Shipment.sender_org_id == Organization.id, isouter=True)
        .group_by(Organization.id)
        .order_by(func.count(Shipment.id).desc())
        .all()
    )
    return [{'organization': name, 'shipments_count': count} for name, count in rows]

@router.get('/workload')
def workload(db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    rows = db.query(Shipment.current_assignee_id, func.count(Shipment.id)).group_by(Shipment.current_assignee_id).all()
    return [{'user_id': user_id, 'active_shipments': count} for user_id, count in rows]
