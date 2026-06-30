from collections.abc import Generator

from sqlmodel import Session, create_engine

from salus.config import settings

engine = create_engine(
    settings.database_url,
    echo=False,
    connect_args={"check_same_thread": False},
)


def get_session() -> Generator[Session]:
    with Session(engine) as session:
        yield session
