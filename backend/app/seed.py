from __future__ import annotations

from collections.abc import Callable, Iterable

from sqlalchemy.orm import Session


SeedOperation = Callable[[Session], None]
SessionFactory = Callable[[], Session]


SEED_OPERATIONS: tuple[SeedOperation, ...] = ()


def run_seed_operations(
    session: Session,
    operations: Iterable[SeedOperation] | None = None,
) -> None:
    """Run registered seed operations inside the caller-managed transaction."""
    for operation in SEED_OPERATIONS if operations is None else operations:
        operation(session)


def seed_database(session_factory: SessionFactory | None = None) -> None:
    """Execute database seed operations manually using the application session."""
    if session_factory is None:
        from app.db import SessionLocal

        session_factory = SessionLocal
    session = session_factory()
    try:
        run_seed_operations(session)
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def main() -> None:
    seed_database()


if __name__ == "__main__":
    main()
