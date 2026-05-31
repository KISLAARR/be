# app/core/config.py
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "Beauty Platform"
    VERSION: str = "0.1.0"
    API_V1_STR: str = "/api/v1"
    
    # Безопасность
    SECRET_KEY: str = "ruMi-supEr-seCreT-kEy-2026-pLeAsE-chAnGe-in-pRoD"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # Токен живёт 24 часа

    # Настройки Базы Данных (как в docker-compose.yml)
    POSTGRES_USER: str = "beauty_user"
    POSTGRES_PASSWORD: str = "beauty_pass_2026"
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: str = "5432"
    POSTGRES_DB: str = "beauty_platform"

    @property
    def DATABASE_URL(self) -> str:
        """Собирает строку подключения для asyncpg"""
        return f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"

    class Config:
        case_sensitive = True

settings = Settings()