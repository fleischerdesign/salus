import secrets

import bcrypt

from salus.models.api_token import ApiToken
from salus.models.user import User
from salus.repositories.unit_of_work import IUnitOfWork

_TOKEN_PREFIX = "sls_"


def _generate_token() -> str:
    raw = secrets.token_urlsafe(24)
    return f"{_TOKEN_PREFIX}{raw}"


class ApiTokenService:
    def __init__(self, uow: IUnitOfWork) -> None:
        self.uow = uow

    def create_token(
        self, user_id: str, label: str, scopes: str = ""
    ) -> tuple[str, ApiToken]:
        plaintext = _generate_token()
        token_hash = bcrypt.hashpw(plaintext.encode(), bcrypt.gensalt()).decode()
        prefix = plaintext[:12]
        token = ApiToken(
            token_hash=token_hash,
            token_prefix=prefix,
            label=label,
            scopes=scopes,
            user_id=user_id,
        )
        self.uow.api_tokens.create(token)
        return plaintext, token

    def resolve(self, token_string: str) -> tuple[User, ApiToken] | None:
        if not token_string.startswith(_TOKEN_PREFIX):
            return None
        prefix = token_string[:12]
        candidates = self.uow.api_tokens.find_by_prefix(prefix)
        for t in candidates:
            if bcrypt.checkpw(token_string.encode(), t.token_hash.encode()):
                self.uow.api_tokens.record_usage(t)
                user = self.uow.users.get_by_id(t.user_id)
                if user is not None:
                    return user, t
        return None

    def list_tokens(self, user_id: str) -> list[ApiToken]:
        return self.uow.api_tokens.find_by_user(user_id)

    def revoke(self, token_id: str, user_id: str) -> None:
        token = self.uow.api_tokens.get_by_id(token_id)
        if token is not None and token.user_id == user_id:
            token.is_active = False
            self.uow.api_tokens.update(token)
