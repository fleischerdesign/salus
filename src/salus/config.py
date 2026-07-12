from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "salus"
    database_url: str = "sqlite:///salus.db"

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

    cors_origins: list[str] = ["http://localhost:5173"]

    llm_provider: str = "ollama"
    llm_api_key: str | None = None
    llm_api_url: str | None = None
    llm_model: str = "llama3"

    backup_password: str | None = None
    backup_provider: str = "local"
    backup_local_dir: str = "data/backups"
    backup_webdav_url: str | None = None
    backup_webdav_username: str | None = None
    backup_webdav_password: str | None = None
    backup_retention_days: int = 14

    model_config = {"env_prefix": "SALUS_"}


settings = Settings()
