"""
Centralized configuration for production deployment.
All sensitive configuration is loaded from environment variables.
"""
import os
from functools import lru_cache
from typing import List

from dotenv import load_dotenv

load_dotenv()


def _parse_origins(origins_str: str) -> List[str]:
    """Parse comma-separated origins string into list."""
    if not origins_str:
        # Default development origins
        return [
            "http://localhost:5173",
            "http://127.0.0.1:5173",
            "http://localhost:5174",
            "http://127.0.0.1:5174",
            "http://localhost:3000",
            "http://127.0.0.1:3000",
        ]
    origins = [origin.strip() for origin in origins_str.split(",") if origin.strip()]
    # If "*" is in the list, allow all origins
    if "*" in origins:
        return ["*"]
    return origins


def _build_origin_regex() -> str:
    """
    Build a regex that matches all Vercel preview/production URLs for this project,
    plus common localhost origins for development.
    """
    return (
        r"^https://hostim-alb-lingo[a-z0-9\-]*\.vercel\.app$"
        r"|^https://.*-ga4444s-projects\.vercel\.app$"
        r"|^http://localhost:\d+$"
        r"|^http://127\.0\.0\.1:\d+$"
    )


class Settings:
    """Application settings loaded from environment variables."""
    
    def __init__(self):
        # Database
        self.DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./dev.db")
        
        # Security
        self.SECRET_KEY: str = os.getenv("SECRET_KEY", "dev-secret-key-change-in-production")
        self.ALGORITHM: str = "HS256"
        self.ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "1440"))  # 24 hours
        
        # CORS - Parse from environment variable
        self.ALLOWED_ORIGINS: List[str] = _parse_origins(os.getenv("ALLOWED_ORIGINS", ""))
        
        # CORS regex - matches all Vercel deployment URLs automatically
        self.ALLOWED_ORIGIN_REGEX: str = _build_origin_regex()
        
        # Environment
        self.ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
        self.DEBUG: bool = os.getenv("DEBUG", "true").lower() == "true"
        
        # Server
        self.HOST: str = os.getenv("HOST", "0.0.0.0")
        self.PORT: int = int(os.getenv("PORT", "8001"))
        
        # AI Services (optional)
        self.OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
        self.ANTHROPIC_API_KEY: str = os.getenv("ANTHROPIC_API_KEY", "")
        self.AZURE_SPEECH_KEY: str = os.getenv("AZURE_SPEECH_KEY", "")
        self.AZURE_SPEECH_REGION: str = os.getenv("AZURE_SPEECH_REGION", "")
    
    @property
    def is_production(self) -> bool:
        return self.ENVIRONMENT == "production"
    
    @property
    def is_sqlite(self) -> bool:
        return self.DATABASE_URL.startswith("sqlite")
    
    @property
    def is_postgres(self) -> bool:
        return self.DATABASE_URL.startswith("postgres")


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()


settings = get_settings()
