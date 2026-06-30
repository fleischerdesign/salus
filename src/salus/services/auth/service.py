from collections.abc import Mapping
from typing import TYPE_CHECKING

from salus.exceptions import InvalidCredentialsError
from salus.models.user import User
from salus.services._helpers import uid
from salus.services.auth.providers import LdapAuthProvider, LocalAuthProvider
from salus.services.jwt import JwtService
from salus.services.user import UserService

if TYPE_CHECKING:
    from salus.services.auth.providers import OidcAuthProvider


class AuthService:
    def __init__(
        self,
        jwt_svc: JwtService,
        user_svc: UserService,
        local_provider: LocalAuthProvider,
        ldap_provider: LdapAuthProvider | None = None,
        oidc_providers: Mapping[str, "OidcAuthProvider"] | None = None,
    ) -> None:
        self._jwt = jwt_svc
        self._user_svc = user_svc
        self._local = local_provider
        self._ldap = ldap_provider
        self._oidc_providers: Mapping[str, "OidcAuthProvider"] = oidc_providers or {}

    def login_local(self, username: str, password: str) -> tuple[str, User]:
        user = self._local.authenticate(username=username, password=password)
        if user is None:
            raise InvalidCredentialsError()
        token = self._jwt.create_token(uid(user), user.username)
        return token, user

    def login_ldap(self, username: str, password: str) -> tuple[str, User]:
        if self._ldap is None:
            raise InvalidCredentialsError("LDAP not configured")
        user = self._ldap.authenticate(username=username, password=password)
        if user is None:
            raise InvalidCredentialsError()
        token = self._jwt.create_token(uid(user), user.username)
        return token, user

    def get_oidc_authorization_url(self, provider_name: str, redirect_uri: str) -> str:
        provider = self._oidc_providers.get(provider_name)
        if provider is None:
            raise ValueError(f"Unknown OIDC provider: {provider_name}")
        return provider.get_authorization_url(redirect_uri)

    def get_oidc_provider(self, name: str) -> "OidcAuthProvider | None":
        return self._oidc_providers.get(name)

    def get_user_from_token(self, token: str) -> User | None:
        payload = self._jwt.verify_token(token)
        if payload is None:
            return None
        user_id = payload.get("sub")
        if user_id is None:
            return None
        return self._user_svc.get_by_id(int(user_id))

    def create_token_for_user(self, user: User) -> str:
        from salus.services._helpers import uid

        return self._jwt.create_token(uid(user), user.username)
