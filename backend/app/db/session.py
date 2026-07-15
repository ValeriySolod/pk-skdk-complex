from sqlalchemy import create_engine
from sqlalchemy.engine import Engine, URL, make_url
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.config import settings


def _is_in_memory_sqlite(database_url: URL) -> bool:
    return database_url.get_backend_name() == "sqlite" and database_url.database in {
        None,
        "",
        ":memory:",
    }


def create_database_engine(database_url_value: str | URL) -> Engine:
    database_url = make_url(database_url_value)
    connect_args = (
        {"check_same_thread": False}
        if database_url.get_backend_name() == "sqlite"
        else {}
    )
    engine_options: dict[str, object] = {}
    if _is_in_memory_sqlite(database_url):
        engine_options["poolclass"] = StaticPool

    return create_engine(
        database_url,
        pool_pre_ping=True,
        connect_args=connect_args,
        **engine_options,
    )


engine = create_database_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
