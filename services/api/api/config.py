"""Configuration settings for the GigPulse AI FastAPI backend."""

import os
from typing import List


class Settings:
    PROJECT_NAME: str = "GigPulse AI"
    PROJECT_DESCRIPTION: str = "Multi-Platform Gig Worker Earnings Intelligence & Demand Forecasting API"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"

    # Database: Supports SQLite path or PostgreSQL connection URL
    DATABASE_PATH: str = os.getenv("DATABASE_URL", os.getenv("GIGPULSE_DB_PATH", "gigpulse.db"))

    # Public Demo Mode: Restricts destructive writes (model retrain, data delete, raw import commit)
    DEMO_MODE: bool = os.getenv("DEMO_MODE", "false").lower() in ("true", "1", "yes")

    # Allowed CORS origins
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "https://*.vercel.app",
        "https://*.onrender.com",
    ]


settings = Settings()
