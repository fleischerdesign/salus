from salus.models.user import User

__all__ = ["uid"]


def uid(user: User) -> int:
    """Return the user's database id, guaranteed present after first persist.

    SQLModel declares `id` as `int | None` because it is absent before
    the initial INSERT.  After `session.flush()` (which `Repository.create()`
    calls internally via `session.commit()` / `session.refresh()`), the
    primary key is always populated.  This helper makes that guarantee
    visible to the type-checker without sprinkling ``# type: ignore[arg-type]``
    through every caller.
    """
    if user.id is None:
        raise ValueError("User has no persisted id — call commit() first")
    return user.id
