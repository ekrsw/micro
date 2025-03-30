import os
from pydantic import BaseSettings
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    PROJECT_NAME: str = "Gateway Service"
    API_V1_STR: str = "/api/v1"
    
    # Auth Service
    AUTH_SERVICE_HOST: str = os.getenv("AUTH_SERVICE_HOST", "localhost")
    AUTH_SERVICE_PORT: int = int(os.getenv("AUTH_SERVICE_PORT", "8000"))
    AUTH_SERVICE_URL: str = f"http://{AUTH_SERVICE_HOST}:{AUTH_SERVICE_PORT}"
    
    # Gateway Service
    HOST: str = os.getenv("GATEWAY_SERVICE_HOST", "localhost")
    PORT: int = int(os.getenv("GATEWAY_SERVICE_PORT", "8001"))
    
    # JWT
    SECRET_KEY: str = os.getenv("AUTH_SECRET_KEY", "supersecretkey")
    ALGORITHM: str = os.getenv("AUTH_ALGORITHM", "HS256")

settings = Settings()
