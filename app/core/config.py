from pydantic import PostgresDsn, SecretStr, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", 
        env_file_encoding="utf-8", 
        extra="ignore",
        case_sensitive=False
    )

    database_url: PostgresDsn
    
    redis_host: str
    redis_port: int = 6379
    redis_schedule_cache_ttl: int = 600
    redis_curr_week_cache_ttl: int = 5000

    mcp_auth_token: SecretStr | None = None
    
    mcp_allowed_origins: list[str] = []

    @field_validator("mcp_allowed_origins", mode="before")
    @classmethod
    def parse_allowed_origins(cls, v: str | list[str]) -> list[str]:
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",") if origin.strip()]
        return v