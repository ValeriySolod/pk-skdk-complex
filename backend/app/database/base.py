from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, metadata, naming_convention


class IntegerPrimaryKeyMixin:
    id: Mapped[int] = mapped_column(primary_key=True)


class AbstractBaseModel(IntegerPrimaryKeyMixin, Base):
    __abstract__ = True
