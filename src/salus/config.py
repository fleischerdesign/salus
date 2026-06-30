import os

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "salus"
    database_url: str = "sqlite:///salus.db"

    hermes_home: str = os.getenv("HERMES_HOME", "data")
    api_token: str = "s3ns0r-h34lth-t0k3n-2026"

    jwt_secret_key: str = "change-me-in-production-salus-2026"
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 1440

    google_client_id: str | None = None
    google_client_secret: str | None = None
    github_client_id: str | None = None
    github_client_secret: str | None = None
    oidc_issuer_url: str | None = None
    oidc_client_id: str | None = None
    oidc_client_secret: str | None = None
    oauth_redirect_base: str = "http://localhost:8000"

    ldap_server_uri: str | None = None
    ldap_base_dn: str | None = None
    ldap_user_dn_template: str = "uid={username},{base_dn}"
    ldap_use_tls: bool = False

    model_config = {"env_prefix": "SALUS_"}


settings = Settings()
