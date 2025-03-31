from typing import Any, Dict, Optional

from pydantic import ConfigDict, Field, PostgresDsn, field_validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    API_V1_STR: str = Field(default="/api/v1")
    SECRET_KEY: str = Field(default="your_secret_key_here", json_schema_extra={"env": "SECRET_KEY"})
    ALGORITHM: str = Field(default="HS256", json_schema_extra={"env": "ALGORITHM"})
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=30, json_schema_extra={"env": "ACCESS_TOKEN_EXPIRE_MINUTES"})
    REFRESH_TOKEN_EXPIRE_HOURS: int = Field(default=24, json_schema_extra={"env": "REFRESH_TOKEN_EXPIRE_HOURS"})
    
    # PostgreSQL設定
    POSTGRES_HOST: str = Field(default="localhost", json_schema_extra={"env": "POSTGRES_HOST"})
    POSTGRES_PORT: int = Field(default=5432, json_schema_extra={"env": "POSTGRES_PORT"})
    POSTGRES_USER: str = Field(default="user", json_schema_extra={"env": "POSTGRES_USER"})
    POSTGRES_PASSWORD: str = Field(default="password", json_schema_extra={"env": "POSTGRES_PASSWORD"})
    POSTGRES_DB: str = Field(default="auth_db", json_schema_extra={"env": "POSTGRES_DB"})
    DATABASE_URL: Optional[str] = None
    ASYNC_DATABASE_URL: Optional[str] = None

    # Admin設定
    ADMIN_USERNAME: str = Field(default="admin", json_schema_extra={"env": "ADMIN_USERNAME"})
    ADMIN_PASSWORD: str = Field(default="password", json_schema_extra={"env": "ADMIN_PASSWORD"})

    @field_validator("DATABASE_URL", mode="before")
    def assemble_db_connection(cls, v: Optional[str], info: Dict[str, Any]) -> Any:
        if isinstance(v, str):
            return v
        
        user = info.data.get("POSTGRES_USER")
        password = info.data.get("POSTGRES_PASSWORD")
        host = info.data.get("POSTGRES_HOST")
        port = info.data.get("POSTGRES_PORT")
        db = info.data.get("POSTGRES_DB")
        
        if not all([user, password, host, db]):
            return None
            
        return f"postgresql://{user}:{password}@{host}:{port}/{db}"

    @field_validator("ASYNC_DATABASE_URL", mode="before")
    def assemble_async_db_connection(cls, v: Optional[str], info: Dict[str, Any]) -> Any:
        if isinstance(v, str):
            return v
            
        user = info.data.get("POSTGRES_USER")
        password = info.data.get("POSTGRES_PASSWORD")
        host = info.data.get("POSTGRES_HOST")
        port = info.data.get("POSTGRES_PORT")
        db = info.data.get("POSTGRES_DB")
        
        if not all([user, password, host, db]):
            return None
            
        return f"postgresql+asyncpg://{user}:{password}@{host}:{port}/{db}"

    model_config = ConfigDict(
        case_sensitive=True,
        env_file=".env"
    )


settings = Settings()
