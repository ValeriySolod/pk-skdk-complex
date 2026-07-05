from __future__ import annotations

from collections.abc import Generator
import os
import sys
from pathlib import Path

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool


BACKEND_DIR = Path(__file__).resolve().parents[1]

if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

os.environ.setdefault("DATABASE_URL", "sqlite+pysqlite:///:memory:")

from app.db.base import Base  # noqa: E402
from app import models as _models  # noqa: E402, F401
from app.modules.organization_structure import (  # noqa: E402, F401
    models as _organization_structure_models,
)
from app.modules.document_management import models as _document_management_models  # noqa: E402, F401
from app.modules.audit_log import models as _audit_log_models  # noqa: E402, F401
from app.modules.user_management import models as _user_management_models  # noqa: E402, F401
from app.modules.file_storage import models as _file_storage_models  # noqa: E402, F401


@pytest.fixture()
def db_session() -> Generator[Session, None, None]:
    engine = create_engine(
        "sqlite+pysqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    TestingSessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)
        engine.dispose()
