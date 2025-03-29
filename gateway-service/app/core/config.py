from typing import List, Union

from pydantic import AnyHttpUrl, field_validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "API Gateway"
    VERSION: str = "0.1.0"
    
    # CORS
    BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = []

    @field_validator("BACKEND_CORS_ORIGINS", mode="before")
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> Union[List[str], str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)

    # Service URLs
    AUTH_SERVICE_URL: str = "http://auth-api:8000"
    USER_SERVICE_URL: str = "http://user-api:8001"
    PRODUCT_SERVICE_URL: str = "http://product-api:8002"

    model_config = {
        "case_sensitive": True,
        "env_file": ".env"
    }


settings = Settings()