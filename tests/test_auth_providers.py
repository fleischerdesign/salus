from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from salus.services.auth.providers import (
    LdapAuthProvider,
    LocalAuthProvider,
    OidcAuthProvider,
)


@pytest.fixture
def mock_user_service():
    svc = MagicMock()
    svc.get_by_username.return_value = None
    svc.register_with_identity.return_value = MagicMock(
        id=1, username="testuser", email="test@example.com"
    )
    return svc


class TestLocalAuthProvider:
    def test_authenticate_success(self, mock_user_service):
        user = MagicMock(password_hash="$2b$12$abcdefghijklmnopqrstuvwxyz")
        mock_user_service.get_by_username.return_value = user

        with patch("salus.services.auth.providers.verify_password", return_value=True):
            provider = LocalAuthProvider(mock_user_service)
            result = provider.authenticate("testuser", "correct_password")

        assert result is user
        mock_user_service.get_by_username.assert_called_once_with("testuser")

    def test_authenticate_wrong_password(self, mock_user_service):
        user = MagicMock(password_hash="$2b$12$abcdefghijklmnopqrstuvwxyz")
        mock_user_service.get_by_username.return_value = user

        with patch("salus.services.auth.providers.verify_password", return_value=False):
            provider = LocalAuthProvider(mock_user_service)
            result = provider.authenticate("testuser", "wrong_password")

        assert result is None

    def test_authenticate_unknown_user(self, mock_user_service):
        mock_user_service.get_by_username.return_value = None

        provider = LocalAuthProvider(mock_user_service)
        result = provider.authenticate("nobody", "any_password")

        assert result is None

    def test_authenticate_no_password_hash(self, mock_user_service):
        user = MagicMock(password_hash=None)
        mock_user_service.get_by_username.return_value = user

        provider = LocalAuthProvider(mock_user_service)
        result = provider.authenticate("testuser", "any_password")

        assert result is None


class TestLdapAuthProvider:
    def test_authenticate_success(self, mock_user_service):
        provider = LdapAuthProvider(
            user_service=mock_user_service,
            server_uri="ldap://localhost:389",
            base_dn="dc=example,dc=com",
        )

        with patch.object(provider, "_try_bind", return_value=True):
            result = provider.authenticate("testuser", "correct_password")

        assert result is not None
        mock_user_service.register_with_identity.assert_called_once_with(
            provider="ldap",
            provider_user_id="uid=testuser,dc=example,dc=com",
            username="testuser",
        )

    def test_authenticate_failed_bind(self, mock_user_service):
        provider = LdapAuthProvider(
            user_service=mock_user_service,
            server_uri="ldap://localhost:389",
            base_dn="dc=example,dc=com",
        )

        with patch.object(provider, "_try_bind", return_value=False):
            result = provider.authenticate("testuser", "wrong_password")

        assert result is None
        mock_user_service.register_with_identity.assert_not_called()

    def test_try_bind_success(self):
        with patch("ldap3.Server"):
            with patch("ldap3.Connection") as MockConnection:
                mock_conn = MagicMock()
                MockConnection.return_value = mock_conn

                provider = LdapAuthProvider(
                    user_service=MagicMock(),
                    server_uri="ldap://localhost:389",
                    base_dn="dc=example,dc=com",
                )
                result = provider._try_bind("ldap://localhost:389", "uid=testuser,dc=example,dc=com", "pass")

                assert result is True
                MockConnection.assert_called_once()
                mock_conn.unbind.assert_called_once()

    def test_try_bind_failure(self):
        with patch("ldap3.Server"):
            with patch(
                "ldap3.Connection",
                side_effect=Exception("Bind failed"),
            ):
                provider = LdapAuthProvider(
                    user_service=MagicMock(),
                    server_uri="ldap://localhost:389",
                    base_dn="dc=example,dc=com",
                )
                result = provider._try_bind("ldap://localhost:389", "uid=testuser,dc=example,dc=com", "pass")

                assert result is False

    def test_try_bind_use_tls(self):
        with patch("ldap3.Server"):
            with patch("ldap3.Connection") as MockConnection:
                mock_conn = MagicMock()
                MockConnection.return_value = mock_conn

                provider = LdapAuthProvider(
                    user_service=MagicMock(),
                    server_uri="ldap://localhost:389",
                    base_dn="dc=example,dc=com",
                    use_tls=True,
                )
                result = provider._try_bind("ldap://localhost:389", "uid=testuser,dc=example,dc=com", "pass")

                assert result is True
                mock_conn.start_tls.assert_called_once()


class TestOidcAuthProvider:
    def _make_mock_oauth(self, mock_client):
        mock_oauth_instance = MagicMock()
        mock_oauth_instance.register = MagicMock()
        mock_oauth_instance.google = mock_client
        mock_oauth_instance.github = mock_client
        return mock_oauth_instance

    def test_get_authorization_url(self):
        mock_client = MagicMock()
        mock_client.authorize_redirect.return_value.url = (
            "https://provider.com/auth?state=xyz"
        )

        with patch(
            "authlib.integrations.starlette_client.OAuth"
        ) as MockOAuth:
            MockOAuth.return_value = self._make_mock_oauth(mock_client)

            provider = OidcAuthProvider(
                name="google",
                issuer_url="https://accounts.google.com",
                client_id="client-id",
                client_secret="client-secret",
                user_service=MagicMock(),
            )

            url = provider.get_authorization_url(
                "http://localhost:8000/auth/callback"
            )

            assert url == "https://provider.com/auth?state=xyz"
            mock_client.authorize_redirect.assert_called_once_with(
                "http://localhost:8000/auth/callback"
            )

    @pytest.mark.asyncio
    async def test_authenticate_success(self, mock_user_service):
        mock_request = MagicMock()
        mock_token = MagicMock()
        mock_token.get.side_effect = lambda key, default=None: {
            "userinfo": {
                "sub": "google-123",
                "email": "user@gmail.com",
                "name": "Test User",
            },
        }.get(key, default)

        mock_client = MagicMock()
        mock_client.authorize_access_token = AsyncMock(return_value=mock_token)

        with patch(
            "authlib.integrations.starlette_client.OAuth"
        ) as MockOAuth:
            MockOAuth.return_value = self._make_mock_oauth(mock_client)

            provider = OidcAuthProvider(
                name="google",
                issuer_url="https://accounts.google.com",
                client_id="client-id",
                client_secret="client-secret",
                user_service=mock_user_service,
            )

            result = await provider.authenticate(mock_request)

            assert result is not None
            mock_user_service.register_with_identity.assert_called_once_with(
                provider="google",
                provider_user_id="google-123",
                email="user@gmail.com",
                display_name="Test User",
            )

    @pytest.mark.asyncio
    async def test_authenticate_no_userinfo(self, mock_user_service):
        mock_request = MagicMock()
        mock_token = MagicMock()
        mock_token.get.return_value = None

        mock_client = MagicMock()
        mock_client.authorize_access_token = AsyncMock(return_value=mock_token)

        with patch(
            "authlib.integrations.starlette_client.OAuth"
        ) as MockOAuth:
            MockOAuth.return_value = self._make_mock_oauth(mock_client)

            provider = OidcAuthProvider(
                name="google",
                issuer_url="https://accounts.google.com",
                client_id="client-id",
                client_secret="client-secret",
                user_service=mock_user_service,
            )

            result = await provider.authenticate(mock_request)

            assert result is None
            mock_user_service.register_with_identity.assert_not_called()

    @pytest.mark.asyncio
    async def test_authenticate_fallback_fields(self, mock_user_service):
        mock_request = MagicMock()
        mock_token = MagicMock()
        mock_token.get.side_effect = lambda key, default=None: {
            "userinfo": {"email": "fallback@example.com"},
        }.get(key, default)

        mock_client = MagicMock()
        mock_client.authorize_access_token = AsyncMock(return_value=mock_token)

        with patch(
            "authlib.integrations.starlette_client.OAuth"
        ) as MockOAuth:
            MockOAuth.return_value = self._make_mock_oauth(mock_client)

            provider = OidcAuthProvider(
                name="github",
                issuer_url="https://github.com",
                client_id="client-id",
                client_secret="client-secret",
                user_service=mock_user_service,
            )

            result = await provider.authenticate(mock_request)

            assert result is not None
            mock_user_service.register_with_identity.assert_called_once_with(
                provider="github",
                provider_user_id="fallback@example.com",
                email="fallback@example.com",
                display_name="fallback@example.com",
            )
