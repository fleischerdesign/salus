from datetime import datetime, timezone

from sqlalchemy import desc
from sqlmodel import select

from salus.models.api_token import ApiToken
from salus.repositories.base import Repository
from salus.repositories.protocols import IApiTokenRepository


class ApiTokenRepository(Repository[ApiToken], IApiTokenRepository):
    model = ApiToken

    def find_by_user(self, user_id: int) -> list[ApiToken]:
        stmt = (
            select(ApiToken)
            .where(ApiToken.user_id == user_id, ApiToken.is_active)
            .order_by(desc(ApiToken.created_at))  # type: ignore
        )
        return list(self.session.exec(stmt).all())

    def find_all_by_user(self, user_id: int) -> list[ApiToken]:
        stmt = select(ApiToken).where(ApiToken.user_id == user_id)
        return list(self.session.exec(stmt).all())

    def find_by_prefix(self, token_prefix: str) -> list[ApiToken]:
        stmt = select(ApiToken).where(
            ApiToken.token_prefix == token_prefix, ApiToken.is_active
        )
        return list(self.session.exec(stmt).all())

    def list_all_active(self) -> list[ApiToken]:
        stmt = (
            select(ApiToken)
            .where(ApiToken.is_active)
            .order_by(desc(ApiToken.created_at))  # type: ignore
        )
        return list(self.session.exec(stmt).all())

    def record_usage(self, token: ApiToken) -> None:
        token.last_used_at = datetime.now(timezone.utc)
        self.update(token)
