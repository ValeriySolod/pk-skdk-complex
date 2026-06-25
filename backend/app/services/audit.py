from sqlalchemy.orm import Session
from app.models import AuditLog, User

def write_audit(db: Session, user: User | None, action: str, entity_type: str, entity_id: str, payload: dict | None = None) -> None:
    db.add(AuditLog(
        user_id=user.id if user else None,
        action=action,
        entity_type=entity_type,
        entity_id=entity_id,
        payload=payload,
    ))
