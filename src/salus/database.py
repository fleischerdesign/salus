from collections.abc import Generator
from urllib.parse import urlparse

from sqlmodel import Session, create_engine

from salus.config import settings


from sqlalchemy import event


def _build_engine(database_url: str):
    parsed = urlparse(database_url)
    if parsed.scheme.startswith("postgresql"):
        return create_engine(database_url, echo=False)
    
    eng = create_engine(
        database_url,
        echo=False,
        connect_args={"check_same_thread": False},
    )

    @event.listens_for(eng, "connect")
    def _set_sqlite_pragma(dbapi_connection, connection_record):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA journal_mode = WAL;")
        cursor.execute("PRAGMA synchronous = NORMAL;")
        cursor.execute("PRAGMA foreign_keys = ON;")
        cursor.close()

    return eng


engine = _build_engine(settings.database_url)


def get_session() -> Generator[Session]:
    with Session(engine) as session:
        yield session
