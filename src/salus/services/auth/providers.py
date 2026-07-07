from salus.models.user import User
from salus.services.password import verify_password
from salus.services.user import UserService


class LocalAuthProvider:
    def __init__(self, user_service: UserService) -> None:
        self._user_svc = user_service

    def authenticate(self, username: str, password: str) -> User | None:
        user = self._user_svc.get_by_username(username)
        if user is None or user.password_hash is None:
            return None
        if not verify_password(password, user.password_hash):
            return None
        return user


class LdapAuthProvider:
    def __init__(
        self,
        user_service: UserService,
        server_uri: str,
        base_dn: str,
        user_dn_template: str = "uid={username},{base_dn}",
        use_tls: bool = False,
    ) -> None:
        self._user_svc = user_service
        self._server_uri = server_uri
        self._base_dn = base_dn
        self._user_dn_template = user_dn_template
        self._use_tls = use_tls

    def authenticate(self, username: str, password: str) -> User | None:
        user_dn = self._user_dn_template.format(
            username=username, base_dn=self._base_dn
        )

        if self._bind(self._server_uri, user_dn, password):
            return self._user_svc.register_with_identity(
                provider="ldap",
                provider_user_id=user_dn,
                username=username,
            )
        return None

    def _bind(self, server_uri: str, user_dn: str, password: str) -> bool:
        from ldap3 import Connection, Server

        try:
            server = Server(server_uri)
            conn = Connection(server, user_dn, password, auto_bind=True)
            if self._use_tls:
                conn.start_tls()
            conn.unbind()
            return True
        except Exception:
            return False


class OidcAuthProvider:
    def __init__(
        self,
        name: str,
        issuer_url: str,
        client_id: str,
        client_secret: str,
        user_service: UserService,
    ) -> None:
        from authlib.integrations.starlette_client import OAuth

        self.name = name
        self._user_svc = user_service
        self._oauth = OAuth()
        self._oauth.register(
            name=name,
            client_id=client_id,
            client_secret=client_secret,
            server_metadata_url=f"{issuer_url}/.well-known/openid-configuration",
            client_kwargs={"scope": "openid email profile"},
        )

    def get_authorization_url(self, redirect_uri: str) -> str:
        client = getattr(self._oauth, self.name)
        return client.authorize_redirect(redirect_uri).url

    async def authenticate(self, request) -> User | None:
        client = getattr(self._oauth, self.name)
        token = await client.authorize_access_token(request)
        userinfo = token.get("userinfo")
        if userinfo is None:
            return None

        provider_user_id = userinfo.get("sub", userinfo.get("email", ""))
        email = userinfo.get("email")
        name = userinfo.get("name", email)

        return self._user_svc.register_with_identity(
            provider=self.name,
            provider_user_id=provider_user_id,
            email=email,
            display_name=name,
        )
