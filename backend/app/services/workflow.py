from datetime import datetime
from app.models import ShipmentStatus

ALLOWED_TRANSITIONS = {
    ShipmentStatus.REGISTERED.value: {ShipmentStatus.ACCEPTED.value},
    ShipmentStatus.ACCEPTED.value: {ShipmentStatus.TRANSIT.value, ShipmentStatus.IN_DELIVERY.value},
    ShipmentStatus.TRANSIT.value: {ShipmentStatus.IN_DELIVERY.value},
    ShipmentStatus.IN_DELIVERY.value: {ShipmentStatus.DELIVERED.value},
    ShipmentStatus.DELIVERED.value: {ShipmentStatus.ARCHIVED.value},
}

def resolve_next_status(current_status: str, requested: str | None = None) -> str:
    if requested:
        if requested not in ALLOWED_TRANSITIONS.get(current_status, set()):
            raise ValueError(f'Неможливий перехід статусу: {current_status} -> {requested}')
        return requested
    next_values = list(ALLOWED_TRANSITIONS.get(current_status, []))
    if not next_values:
        raise ValueError(f'Для статусу {current_status} немає автоматичного наступного етапу')
    return next_values[0]

def apply_delivery_timestamps(shipment) -> None:
    if shipment.status == ShipmentStatus.ACCEPTED.value and shipment.accepted_at is None:
        shipment.accepted_at = datetime.utcnow()
    if shipment.status == ShipmentStatus.DELIVERED.value and shipment.delivered_at is None:
        shipment.delivered_at = datetime.utcnow()
