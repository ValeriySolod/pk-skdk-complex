from collections.abc import Generator

from sqlalchemy.orm import Session

from app.db.session import SessionLocal


def get_db() -> Generator[Session, None, None]:
    """Provide a database session for FastAPI request dependencies.

    The yielded session is closed after the request dependency scope finishes,
    ensuring connections are returned to the SQLAlchemy connection pool.
    """
    db = SessionLocal()
    try:
        yield db
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()
