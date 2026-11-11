"""
Core configuration and application settings.
"""
from pydantic_settings import BaseSettings
from pydantic import Field
from typing import Optional
import os


class Settings(BaseSettings):
    PROJECT_NAME: str = "AI-Assisted Vendor Risk Classification and Trust Assessment System"
    API_V1_PREFIX: str = "/api/v1"
    DATABASE_URL: str = Field(
        default="postgresql://postgres:postgres@localhost:5432/vendor_risk_db",
        description="PostgreSQL Connection URL"
    )
    FALLBACK_SQLITE_URL: str = "sqlite:///./vendor_risk_local.db"
    DEBUG: bool = True

    # Weights for the 5 risk dimensions (specified by proposal)
    WEIGHT_FINANCIAL: float = 0.25
    WEIGHT_SECURITY: float = 0.25
    WEIGHT_COMPLIANCE: float = 0.20
    WEIGHT_OPERATIONAL: float = 0.20
    WEIGHT_REPUTATION: float = 0.10

    # Prototype Implementation Thresholds (0-39 Low, 40-69 Medium, 70-100 High)
    THRESHOLD_LOW_MAX: float = 39.0
    THRESHOLD_MEDIUM_MAX: float = 69.0

    # Phase 2: Document Ingestion, Processing & Vector Storage
    MAX_UPLOAD_SIZE_BYTES: int = 25 * 1024 * 1024  # 25 MB
    UPLOAD_DIR: str = "data/uploads"
    CHROMA_PERSIST_DIRECTORY: str = "./chroma_db"
    TESSERACT_CMD: Optional[str] = None
    SUPPORTED_EXTENSIONS: list[str] = [".pdf", ".docx", ".txt", ".csv"]

    # Phase 2: Chunking Configuration
    CHUNK_SIZE_TOKENS: int = 800
    CHUNK_OVERLAP_TOKENS: int = 150

    class Config:
        env_file = ".env"
        extra = "ignore"


settings = Settings()
