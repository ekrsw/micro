import os
from typing import Any, Dict, Optional

from pydantic import PostgresDsn, field_validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your_secret_key_here")
    ALGORITHM: str = os.getenv("ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
    
    # PostgreSQL設定
    POSTGRES_SERVER: str = os.getenv("POSTGRES_SERVER", "db")
    POSTGRES_USER: str = os.getenv("POSTGRES_USER", "user")
    POSTGRES_PASSWORD: str = os.getenv("POSTGRES_PASSWORD", "password")
    POSTGRES_DB: str = os.getenv("POSTGRES_DB", "auth_db")
    DATABASE_URL: Optional[PostgresDsn] = os.getenv("DATABASE_URL")
    ASYNC_DATABASE_URL: Optional[str] = None

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

    class Config:
        case_sensitive = True
        env_file = ".env"


settings = Settings()
