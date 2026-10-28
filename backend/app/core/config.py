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
    EMBEDDING_PROVIDER: str = os.getenv("EMBEDDING_PROVIDER", "auto")
    BGE_M3_MODEL: str = os.getenv("BGE_M3_MODEL", "BAAI/bge-m3")
    CHROMA_DB_DIR: str = os.getenv("CHROMA_DB_DIR", "./chroma_storage")

    # Live supplier and payment adapters are opt-in.  Without credentials the
    # UI remains in clearly labelled quote/sandbox mode; it never presents a
    # simulated provider response as a confirmed commercial booking.
    DUFFEL_ACCESS_TOKEN: str = os.getenv("DUFFEL_ACCESS_TOKEN", "")
    AMADEUS_CLIENT_ID: str = os.getenv("AMADEUS_CLIENT_ID", "")
    AMADEUS_CLIENT_SECRET: str = os.getenv("AMADEUS_CLIENT_SECRET", "")
    GOOGLE_PLACES_API_KEY: str = os.getenv("GOOGLE_PLACES_API_KEY", "")
    OPENWEATHER_API_KEY: str = os.getenv("OPENWEATHER_API_KEY", "")
    STRIPE_SECRET_KEY: str = os.getenv("STRIPE_SECRET_KEY", "")
    STRIPE_WEBHOOK_SECRET: str = os.getenv("STRIPE_WEBHOOK_SECRET", "")
    VNPAY_TMN_CODE: str = os.getenv("VNPAY_TMN_CODE", "")
    VNPAY_HASH_SECRET: str = os.getenv("VNPAY_HASH_SECRET", "")
    MOMO_PARTNER_CODE: str = os.getenv("MOMO_PARTNER_CODE", "")
    MOMO_ACCESS_KEY: str = os.getenv("MOMO_ACCESS_KEY", "")
    MOMO_SECRET_KEY: str = os.getenv("MOMO_SECRET_KEY", "")
    PAYMENT_SANDBOX: bool = os.getenv("PAYMENT_SANDBOX", "true").lower() == "true"
    
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
