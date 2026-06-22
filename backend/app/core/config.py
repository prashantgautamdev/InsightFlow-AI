"""
Application configuration.
All values are loaded from environment variables (see .env.example).
"""
from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # ---- App ----
    APP_NAME: str = "InsightFlow AI"
    APP_ENV: str = "development"
    DEBUG: bool = True
    API_V1_PREFIX: str = "/api/v1"
    FRONTEND_URL: str = "http://localhost:5173"

    # ---- Security ----
    SECRET_KEY: str = "CHANGE_ME_IN_PRODUCTION"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24       # 1 day
    REFRESH_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days
    EMAIL_VERIFICATION_TOKEN_EXPIRE_MINUTES: int = 60 * 24

    # ---- Database ----
    DATABASE_URL: str = (
        "postgresql://insightflow:insightflow@localhost:5432/insightflow_db"
    )

    # ---- Redis / Celery ----
    REDIS_URL: str = "redis://localhost:6379/0"
    CELERY_BROKER_URL: str = "redis://localhost:6379/1"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/2"

    # ---- AI Providers ----
    OPENAI_API_KEY: str = ""
    GEMINI_API_KEY: str = ""
    DEFAULT_AI_PROVIDER: str = "gemini"  # "gemini" | "openai"

    # ---- ChromaDB ----
    CHROMA_PERSIST_DIR: str = "./chroma_store"

    # ---- Email (SMTP) ----
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""
    EMAILS_FROM_EMAIL: str = "noreply@insightflow.ai"

    # ---- File Uploads ----
    MAX_UPLOAD_SIZE_MB: int = 25
    UPLOAD_DIR: str = "./uploads"
    ALLOWED_RESUME_EXTENSIONS: List[str] = [".pdf"]
    ALLOWED_DATASET_EXTENSIONS: List[str] = [".csv", ".xlsx", ".xls"]

    # ---- CORS ----
    CORS_ORIGINS: List[str] = ["http://localhost:5173", "http://localhost:3000"]

    # ---- Rate Limiting ----
    RATE_LIMIT_DEFAULT: str = "100/minute"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
