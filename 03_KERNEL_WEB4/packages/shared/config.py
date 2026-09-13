"""Configuration management via environment variables."""

from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Engine
    engine_name: str = Field(default="WEB4_BLACK_MUCIZEWORK")
    engine_mode: str = Field(default="BLACK")
    api_version: str = Field(default="1.0")
    port: int = Field(default=5002)

    # Security
    jwt_secret: str = Field(default="MUCIZEWORK_SECRET_KEY")
    cors_origins: str = Field(default="*")

    # Storage
    database_url: str = Field(default="json://storage/db/db.json")

    # Solana
    rpc_url: str = Field(default="https://api.devnet.solana.com")

    # Redis
    redis_url: str = Field(default="")

    # Observability
    log_level: str = Field(default="INFO")
    log_format: str = Field(default="json")

    model_config = {"env_prefix": "MZC_", "env_file": ".env", "extra": "ignore"}


@lru_cache
def get_settings() -> Settings:
    return Settings()
