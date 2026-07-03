from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from app.db.dependencies import get_db
from app.services.database import DatabaseHealthService

router = APIRouter(prefix="/health", tags=["health"])


@router.get("/database")
def database_health(db: Session = Depends(get_db)):
    health_status = DatabaseHealthService(db).check_connection()
    if health_status.is_healthy:
        return health_status.as_response()

    return JSONResponse(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        content=health_status.as_response(),
    )
