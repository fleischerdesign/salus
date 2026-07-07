import os

from salus.config import settings as app_settings
from salus.exceptions import ConflictError
from salus.models.system_config import SystemConfig
from salus.repositories.protocols import ISystemConfigRepository

CONFIG_DEFINITIONS = [
    ("app_name", "Application name", "general", False),
    ("jwt_secret_key", "JWT signing key", "security", True),
    ("jwt_algorithm", "JWT algorithm", "security", False),
    ("jwt_expire_minutes", "JWT expiry (minutes)", "security", False),
    ("api_token", "Global API token (webhook fallback)", "security", True),
    ("google_client_id", "Google OAuth client ID", "oidc", True),
    ("google_client_secret", "Google OAuth client secret", "oidc", True),
    ("github_client_id", "GitHub OAuth client ID", "oidc", True),
    ("github_client_secret", "GitHub OAuth client secret", "oidc", True),
    ("oidc_issuer_url", "OIDC issuer URL", "oidc", False),
    ("oidc_client_id", "OIDC client ID", "oidc", True),
    ("oidc_client_secret", "OIDC client secret", "oidc", True),
    ("ldap_server_uri", "LDAP server URI", "ldap", False),
    ("ldap_base_dn", "LDAP base DN", "ldap", False),
    ("ldap_user_dn_template", "LDAP user DN template", "ldap", False),
    ("ldap_use_tls", "LDAP use TLS", "ldap", False),
    (
        "llm_provider",
        "LLM Provider (ollama/openai/anthropic/deepseek/openrouter)",
        "llm",
        False,
    ),
    ("llm_api_key", "LLM API Key", "llm", True),
    ("llm_api_url", "LLM API Base URL (optional)", "llm", False),
    ("llm_model", "LLM Model name", "llm", False),
]

CATEGORY_ORDER = ["general", "security", "oidc", "ldap", "llm"]


class ConfigService:
    def __init__(self, repo: ISystemConfigRepository) -> None:
        self._repo = repo

    def seed_defaults(self) -> int:
        items: list[SystemConfig] = []
        for key, desc, cat, secret in CONFIG_DEFINITIONS:
            default_value = getattr(app_settings, key, "")
            if default_value is None:
                default_value = ""
            items.append(
                SystemConfig(
                    key=key,
                    value=str(default_value),
                    description=desc,
                    category=cat,
                    is_secret=secret,
                )
            )
        return self._repo.seed_missing(items)

    def _env_var_name(self, key: str) -> str:
        return f"SALUS_{key.upper()}"

    def is_env_override(self, key: str) -> bool:
        return self._env_var_name(key) in os.environ

    def get_resolved_value(self, key: str) -> str:
        env_var = self._env_var_name(key)
        if env_var in os.environ:
            return os.environ[env_var]
        config = self._repo.get_by_key(key)
        return config.value if config else ""

    def get_all(self) -> list[dict]:
        db_configs = {c.key: c for c in self._repo.get_all()}
        result: list[dict] = []
        for key, desc, cat, secret in CONFIG_DEFINITIONS:
            env_override = self.is_env_override(key)
            db_config = db_configs.get(key)
            result.append(
                {
                    "key": key,
                    "description": desc,
                    "category": cat,
                    "is_secret": secret,
                    "is_env_override": env_override,
                    "value": self.get_resolved_value(key),
                    "db_has_value": db_config is not None,
                    "env_var_name": self._env_var_name(key),
                }
            )
        return result

    def set(self, key: str, value: str) -> SystemConfig:
        if self.is_env_override(key):
            raise ConflictError(
                f"{key} is set via {self._env_var_name(key)} environment variable"
            )
        desc = ""
        cat = "general"
        secret = False
        for k, d, c, s in CONFIG_DEFINITIONS:
            if k == key:
                desc, cat, secret = d, c, s
                break
        return self._repo.upsert(
            key, value, description=desc, category=cat, is_secret=secret
        )
