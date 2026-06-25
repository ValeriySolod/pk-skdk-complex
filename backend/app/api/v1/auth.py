from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import create_access_token, get_current_user, verify_password
from app.models import User
from app.schemas.auth import Token, UserRead

router = APIRouter(prefix='/auth', tags=['Авторизація'])

@router.post('/login', response_model=Token)
def login(form: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == form.username).first()
    if not user or not verify_password(form.password, user.password_hash):
        raise HTTPException(status_code=401, detail='Невірний логін або пароль')
    return Token(access_token=create_access_token(str(user.id), user.role))

@router.get('/me', response_model=UserRead)
def me(user: User = Depends(get_current_user)):
    return user
