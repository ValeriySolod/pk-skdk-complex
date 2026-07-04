from __future__ import annotations

from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class Document(Base):
    """Document metadata placeholder."""

    __tablename__ = "documents"

    id: Mapped[int] = mapped_column(primary_key=True)


class DocumentVersion(Base):
    """Document version placeholder."""

    __tablename__ = "document_versions"

    id: Mapped[int] = mapped_column(primary_key=True)


class DocumentCategory(Base):
    """Document category placeholder."""

    __tablename__ = "document_categories"

    id: Mapped[int] = mapped_column(primary_key=True)
