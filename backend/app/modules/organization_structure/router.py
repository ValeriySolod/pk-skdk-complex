from fastapi import APIRouter, Depends

from app.core.security import get_current_user
from app.models import User


router = APIRouter()


@router.get("/health")
def module_health(_: User = Depends(get_current_user)):
    return {"status": "ok"}

