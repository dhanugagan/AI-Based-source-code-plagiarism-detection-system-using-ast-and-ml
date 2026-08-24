"""
Application configuration.

All secrets and environment-specific values are loaded from environment
variables (via a .env file in development). Nothing sensitive is hard-coded.
"""
import os
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=str(BASE_DIR / ".env"), extra="ignore")

    DATABASE_URL: str = "sqlite:///./plagiarism.db"
    SECRET_KEY: str = "insecure-dev-secret-change-me"
    JWT_SECRET: str = "insecure-dev-jwt-secret-change-me"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    UPLOAD_DIRECTORY: str = "../uploads"
    REPORT_DIRECTORY: str = "../reports"
    MODEL_PATH: str = "../models/plagiarism_model.joblib"

    CORS_ORIGINS: str = "http://localhost:5173,http://localhost:3000"
    MAX_FILE_SIZE_MB: int = 2

    # Scoring weights (configurable, not assumed optimal — see README)
    WEIGHT_AST: float = 0.40
    WEIGHT_TOKEN: float = 0.20
    WEIGHT_STRUCTURAL: float = 0.20
    WEIGHT_ML: float = 0.20

    # Risk thresholds (percent)
    RISK_LOW_MAX: int = 30
    RISK_MEDIUM_MAX: int = 60
    RISK_HIGH_MAX: int = 80

    @property
    def cors_origins_list(self):
        return [o.strip() for o in self.CORS_ORIGINS.split(",") if o.strip()]


settings = Settings()

# Ensure runtime directories exist
for d in (settings.UPLOAD_DIRECTORY, settings.REPORT_DIRECTORY, os.path.dirname(settings.MODEL_PATH) or "."):
    Path(d).mkdir(parents=True, exist_ok=True)
