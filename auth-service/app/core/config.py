from typing import Any, Dict, Optional

from pydantic import ConfigDict, Field, PostgresDsn, field_validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    API_V1_STR: str = Field(default="/api/v1")
    SECRET_KEY: str = Field(default="your_secret_key_here", json_schema_extra={"env": "SECRET_KEY"})
    ALGORITHM: str = Field(default="HS256", json_schema_extra={"env": "ALGORITHM"})
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=30, json_schema_extra={"env": "ACCESS_TOKEN_EXPIRE_MINUTES"})
    
    # PostgreSQL設定
    POSTGRES_SERVER: str = Field(default="db", json_schema_extra={"env": "POSTGRES_SERVER"})
    POSTGRES_USER: str = Field(default="user", json_schema_extra={"env": "POSTGRES_USER"})
    POSTGRES_PASSWORD: str = Field(default="password", json_schema_extra={"env": "POSTGRES_PASSWORD"})
    POSTGRES_DB: str = Field(default="auth_db", json_schema_extra={"env": "POSTGRES_DB"})
    DATABASE_URL: Optional[PostgresDsn] = Field(default=None, json_schema_extra={"env": "DATABASE_URL"})
    ASYNC_DATABASE_URL: Optional[str] = None

    # Admin設定
    ADMIN_USERNAME: str = Field(default="admin", json_schema_extra={"env": "ADMIN_USERNAME"})
    ADMIN_PASSWORD: str = Field(default="password", json_schema_extra={"env": "ADMIN_PASSWORD"})

    @field_validator("DATABASE_URL", mode="before")
    def assemble_db_connection(cls, v: Optional[str], values: Dict[str, Any]) -> Any:
        if isinstance(v, str):
            return v
        return PostgresDsn.build(
            scheme="postgresql",
            username=values.data.get("POSTGRES_USER"),
            password=values.data.get("POSTGRES_PASSWORD"),
            host=values.data.get("POSTGRES_SERVER"),
            path=f"{values.data.get('POSTGRES_DB') or ''}",
        )

    @field_validator("ASYNC_DATABASE_URL", mode="before")
    def assemble_async_db_connection(cls, v: Optional[str], values: Dict[str, Any]) -> Any:
        if isinstance(v, str):
            return v
        db_url = values.data.get("DATABASE_URL")
        if db_url:
            # PostgreSQLの接続URLを非同期用に変更
            return str(db_url).replace("postgresql://", "postgresql+asyncpg://")
        return None

    model_config = ConfigDict(
        case_sensitive=True,
        env_file=".env"
    )


settings = Settings()
