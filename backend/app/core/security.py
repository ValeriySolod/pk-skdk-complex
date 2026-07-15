from datetime import datetime, timedelta, timezone
from typing import Iterable
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from .config import settings
from app.db import get_db
from app.models.user import User, Role

pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')
oauth2_scheme = OAuth2PasswordBearer(tokenUrl='/api/v1/auth/login')

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(password: str, hashed: str) -> bool:
    return pwd_context.verify(password, hashed)

def create_access_token(subject: str, role: str) -> str:
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    payload = {'sub': subject, 'role': role, 'exp': expire}
    return jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail='Не вдалося підтвердити облікові дані',
        headers={'WWW-Authenticate': 'Bearer'},
    )
    try:
        payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
        user_id = payload.get('sub')
        if user_id is None:
            raise credentials_exception
    except JWTError as exc:
        raise credentials_exception from exc
    user = db.get(User, int(user_id))
    if user is None or not user.is_active:
        raise credentials_exception
    return user

def require_roles(allowed: Iterable[Role]):
    allowed_values = {role.value for role in allowed}
    def dependency(user: User = Depends(get_current_user)) -> User:
        if user.role not in allowed_values:
            raise HTTPException(status_code=403, detail='Недостатньо прав доступу')
        return user
    return dependency
