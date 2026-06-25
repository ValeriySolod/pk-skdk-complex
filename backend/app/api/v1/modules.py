from fastapi import APIRouter
from app.core.module_registry import registry

router = APIRouter(prefix='/modules', tags=['Модулі'])

@router.get('')
def list_modules():
    return registry.list()
