from typing import Any, Dict, Optional

from pydantic import ConfigDict, Field, PostgresDsn, field_validator, AnyUrl
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
    
    # Redis設定
    REDIS_HOST: str = Field(default="localhost", json_schema_extra={"env": "REDIS_HOST"})
    REDIS_PORT: int = Field(default=6379, json_schema_extra={"env": "REDIS_PORT"})
    REDIS_DB: int = Field(default=0, json_schema_extra={"env": "REDIS_DB"})
    REDIS_PASSWORD: Optional[str] = Field(default=None, json_schema_extra={"env": "REDIS_PASSWORD"})
    REDIS_URL: Optional[str] = None
    
    # トークン設定
    ACCESS_TOKEN_REDIS_EXPIRE_SECONDS: int = Field(default=1800, json_schema_extra={"env": "ACCESS_TOKEN_REDIS_EXPIRE_SECONDS"})  # 30分をデフォルトとする

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
    
    @field_validator("REDIS_URL", mode="before")
    def assemble_redis_connection(cls, v: Optional[str], info: Dict[str, Any]) -> Any:
        if isinstance(v, str):
            return v
            
        host = info.data.get("REDIS_HOST")
        port = info.data.get("REDIS_PORT")
        db = info.data.get("REDIS_DB")
        password = info.data.get("REDIS_PASSWORD")
        
        if not host:
            return None
            
        if password:
            return f"redis://:{password}@{host}:{port}/{db}"
        else:
            return f"redis://{host}:{port}/{db}"
    
    @field_validator("ACCESS_TOKEN_REDIS_EXPIRE_SECONDS", mode="before")
    def convert_minutes_to_seconds(cls, v: Optional[int], info: Dict[str, Any]) -> Any:
        if v is not None:
            return v
        
        # 環境変数から取得
        seconds = info.data.get("ACCESS_TOKEN_REDIS_EXPIRE_SECONDS")
        if seconds is None:
            return 1800  # デフォルト30分
        
        return seconds

    model_config = ConfigDict(
        case_sensitive=True,
        env_file=".env"
    )


settings = Settings()
