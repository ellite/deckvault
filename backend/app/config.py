import sys
from pydantic_settings import BaseSettings

_INSECURE_DEFAULTS = {"change-me-in-production", "change-me-generate-a-random-string", ""}


class Settings(BaseSettings):
    database_url: str = "sqlite:///./data/deckVault.db"
    secret_key: str = "change-me-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60 * 24 * 7  # 7 days
    cookie_secure: bool = False  # set True when serving over HTTPS
    docs_enabled: bool = False

    model_config = {"env_file": ".env"}


settings = Settings()

if settings.secret_key in _INSECURE_DEFAULTS:
    print(
        "FATAL: SECRET_KEY is set to the default insecure value. "
        "Set a random SECRET_KEY environment variable before starting.",
        file=sys.stderr,
    )
    sys.exit(1)
