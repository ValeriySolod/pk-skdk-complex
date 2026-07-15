from enum import Enum
from sqlalchemy import Boolean, String
from sqlalchemy.orm import Mapped, mapped_column
from app.db import Base

class Role(str, Enum):
    GU_HEAD = 'ГУУФЗ Начальник'
    GU_INTAKE = 'ГУУФЗ Дільниця приймання відправлень'
    GU_UKRAINE = 'ГУУФЗ Дільниця Україна'
    GU_KYIV = 'ГУУФЗ Дільниця Київ'
    GU_SECRET = 'ГУУФЗ Секретна дільниця'
    GU_CONTROLLERS = 'ГУУФЗ Контролери'
    GU_DUTY = 'ГУУФЗ Черговий експедиції'
    UFZ_PROCESSING = 'УФЗ Дільниця обробки відправлень'
    UFZ_HEAD = 'УФЗ Начальник'
    UFZ_CONTROLLERS = 'УФЗ Контролери'
    SYSTEM_ADMIN = 'Адміністратори системи'
    NODE_ADMIN = 'Адміністратори вузла'

class User(Base):
    __tablename__ = 'users'
    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(80), unique=True, index=True)
    full_name: Mapped[str] = mapped_column(String(200))
    password_hash: Mapped[str] = mapped_column(String(255))
    role: Mapped[str] = mapped_column(String(120), index=True)
    department: Mapped[str | None] = mapped_column(String(160), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
