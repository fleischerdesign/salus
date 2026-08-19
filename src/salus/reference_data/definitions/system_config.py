"""System configuration reference definitions."""

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
    ("food_off_enabled", "OpenFoodFacts barcode lookup enabled", "food", False),
]

CATEGORY_ORDER = ["general", "security", "oidc", "ldap", "llm", "food"]
