import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "AI Travel Agent API"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    
    SECRET_KEY: str = os.getenv("SECRET_KEY", "super_secret_jwt_key_travel_agent_2026_antigravity")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7 # 7 days
    REFRESH_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 30 # 30 days
    
    # SQLite default for easy running out of the box, configurable to PostgreSQL/MySQL
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./travel_agent.db")
    
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    
    CHROMA_DB_DIR: str = os.getenv("CHROMA_DB_DIR", "./chroma_storage")
    
    # Allowed CORS Origins for Web, Mobile, and local dev
    CORS_ORIGINS: list[str] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:8081",
        "http://127.0.0.1:8081",
        "http://localhost:19006",
        "http://127.0.0.1:19006",
        "*"
    ]

    class Config:
        case_sensitive = True

settings = Settings()
