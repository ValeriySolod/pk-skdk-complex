from fastapi import Depends, FastAPI, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.db.dependencies import get_db
from app.services.database import DatabaseHealthService
from sqlalchemy.orm import Session
from app.core.database import Base, engine
from app.api.v1.auth import router as auth_router
from app.api.v1.modules import router as modules_router
import app.modules_loader  # noqa: F401
from app.core.module_registry import registry

Base.metadata.create_all(bind=engine)

app = FastAPI(title=settings.APP_NAME, version='0.1.0')
app.add_middleware(
    CORSMiddleware,
    allow_origins=['http://localhost:5173', 'http://127.0.0.1:5173'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)

api = APIRouter(prefix='/api/v1')
api.include_router(auth_router)
api.include_router(modules_router)
registry.include_all(api)
app.include_router(api)

@app.get('/health')
def health():
    return {'status': 'ok', 'app': settings.APP_NAME}


@app.get('/health/db')
def database_health(db: Session = Depends(get_db)):
    DatabaseHealthService(db).check_connection()
    return {'status': 'ok', 'database': 'connected'}
