import json
import os
from pathlib import Path
from typing import List, Union
from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

# Determine project directories
BACKEND_DIR = Path(__file__).resolve().parent.parent.parent
PROJECT_ROOT = BACKEND_DIR.parent

# Detect active environment
ENV_MODE = os.getenv("ENVIRONMENT", "development").lower()
if "test" in ENV_MODE:
    env_file_name = ".env.test"
elif "prod" in ENV_MODE:
    env_file_name = ".env.prod"
else:
    env_file_name = ".env.dev"

# Look for env file in backend folder first, then project root
env_path = BACKEND_DIR / env_file_name
if not env_path.exists():
    env_path = PROJECT_ROOT / env_file_name
if not env_path.exists():
    env_path = BACKEND_DIR / ".env"

class Settings(BaseSettings):
    ENVIRONMENT: str = "development"
    PROJECT_NAME: str = "AI BusinessOS"
    API_V1_STR: str = "/api/v1"

    # JWT Config
    JWT_SECRET_KEY: str
    JWT_REFRESH_SECRET_KEY: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # DB Config
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "postgrespassword"
    POSTGRES_DB: str = "ai_businessos"
    POSTGRES_HOST: str = "db"
    POSTGRES_PORT: str = "5432"
    DATABASE_URL: str

    # Redis Config
    REDIS_URL: str = "redis://redis:6379/0"

    # CORS Configuration
    CORS_ORIGINS: List[str] = ["http://localhost:5173", "http://localhost:3000"]

    # Initial Seeds
    FIRST_SUPER_ADMIN_EMAIL: str = "superadmin@businessos.com"
    FIRST_SUPER_ADMIN_PASSWORD: str = "SuperSecurePassword123!"

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> List[str]:
        if isinstance(v, str):
            if v.startswith("[") and v.endswith("]"):
                try:
                    return json.loads(v)
                except Exception:
                    pass
            return [i.strip() for i in v.split(",") if i.strip()]
        return v

    model_config = SettingsConfigDict(
        env_file=env_path if env_path.exists() else None,
        env_file_encoding="utf-8",
        extra="ignore",
    )

settings = Settings()
