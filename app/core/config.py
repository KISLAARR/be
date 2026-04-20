# app/core/config.py
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "Beauty Platform"
    VERSION: str = "0.1.0"
    API_V1_STR: str = "/api/v1"
    
    # Настройки Базы Данных (совпадают с docker-compose)
    POSTGRES_USER: str = "beauty_user"
    POSTGRES_PASSWORD: str = "beauty_pass_2026"
    POSTGRES_HOST: str = "127.0.0.1"  # Важно: именно 127.0.0.1, а не localhost
    POSTGRES_PORT: str = "5433"
    POSTGRES_DB: str = "beauty_platform"
    
    @property
    def DATABASE_URL(self) -> str:
        """Собирает строку подключения для asyncpg"""
        return f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
    
    class Config:
        case_sensitive = True

settings = Settings()