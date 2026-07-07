import secrets

import bcrypt

from salus.models.api_token import ApiToken
from salus.models.user import User
from salus.repositories.protocols import IApiTokenRepository, IUserRepository

_TOKEN_PREFIX = "sls_"


def _generate_token() -> str:
    raw = secrets.token_urlsafe(24)
    return f"{_TOKEN_PREFIX}{raw}"


class ApiTokenService:
    def __init__(self, repo: IApiTokenRepository, user_repo: IUserRepository) -> None:
        self._repo = repo
        self._user_repo = user_repo

    def create_token(
        self, user_id: int, label: str, scopes: str = ""
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
        self._repo.create(token)
        return plaintext, token

    def resolve(self, token_string: str) -> tuple[User, ApiToken] | None:
        if not token_string.startswith(_TOKEN_PREFIX):
            return None
        prefix = token_string[:12]
        candidates = self._repo.find_by_prefix(prefix)
        for t in candidates:
            if bcrypt.checkpw(token_string.encode(), t.token_hash.encode()):
                self._repo.record_usage(t)
                user = self._user_repo.get_by_id(t.user_id)
                if user is not None:
                    return user, t
        return None

    def list_tokens(self, user_id: int) -> list[ApiToken]:
        return self._repo.find_by_user(user_id)

    def revoke(self, token_id: int, user_id: int) -> None:
        token = self._repo.get_by_id(token_id)
        if token is not None and token.user_id == user_id:
            token.is_active = False
            self._repo.update(token)
