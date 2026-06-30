from collections.abc import Generator
from urllib.parse import urlparse

from sqlmodel import Session, create_engine

from salus.config import settings


def _build_engine(database_url: str):
    parsed = urlparse(database_url)
    if parsed.scheme.startswith("postgresql"):
        return create_engine(database_url, echo=False)
    return create_engine(
        database_url,
        echo=False,
        connect_args={"check_same_thread": False},
    )


engine = _build_engine(settings.database_url)


def get_session() -> Generator[Session]:
    with Session(engine) as session:
        yield session
