import pytest
from sqlalchemy.pool import StaticPool
from sqlmodel import Session, SQLModel, create_engine, select

from salus.models.user import User
from salus.repositories.unit_of_work import SqlUnitOfWork


@pytest.fixture
def session():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)
    with Session(engine) as s:
        yield s


def test_uow_commit(session: Session):
    uow = SqlUnitOfWork(session)
    with uow:
        u = User(username="uow_user", password_hash="hash", display_name="UoW")
        uow.users.add(u)

    db_user = session.exec(select(User).where(User.username == "uow_user")).first()
    assert db_user is not None
    assert db_user.display_name == "UoW"


def test_uow_rollback_on_exception(session: Session):
    uow = SqlUnitOfWork(session)
    try:
        with uow:
            u = User(username="uow_rollback_user", password_hash="hash", display_name="Rollback")
            uow.users.add(u)
            raise ValueError("Forced error")
    except ValueError:
        pass

    db_user = session.exec(select(User).where(User.username == "uow_rollback_user")).first()
    assert db_user is None
