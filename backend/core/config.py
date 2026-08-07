# -*- coding: utf-8 -*-
"""Global application configuration settings."""

import os
from pathlib import Path
from typing import List
from pydantic import BaseModel, Field

# Base directories
BASE_DIR = Path(__file__).resolve().parent.parent

class Settings(BaseModel):
    """Global configuration settings for ACPIA."""
    
    # Environment
    ENVIRONMENT: str = Field(default_factory=lambda: os.getenv("ACPIA_ENV", "development"))
    DEBUG: bool = Field(default_factory=lambda: os.getenv("ACPIA_DEBUG", "true").lower() == "true")
    
    # Versioning
    VERSION: str = "1.0.0"
    
    # Paths
    STORAGE_DIR: Path = Field(
        default_factory=lambda: Path(os.getenv("ACPIA_STORAGE_DIR", str(BASE_DIR / "storage")))
    )
    DATABASE_URL: str = Field(
        default_factory=lambda: os.getenv(
            "ACPIA_DATABASE_URL", f"sqlite:///{BASE_DIR / 'acpia.db'}"
        )
    )
    
    # Limits & Allowed MIME Types
    MAX_FILE_SIZE_BYTES: int = Field(
        default_factory=lambda: int(os.getenv("ACPIA_MAX_FILE_SIZE_BYTES", str(100 * 1024 * 1024))) # 100MB
    )
    ALLOWED_MIME_TYPES: List[str] = Field(
        default_factory=lambda: [
            # Images
            "image/jpeg",
            "image/png",
            "image/gif",
            "image/webp",
            # Documents / PDFs
            "application/pdf",
            "text/plain",
            "application/json",
            # Audio
            "audio/mpeg",
            "audio/wav",
            "audio/ogg",
            "audio/x-wav",
            # Video
            "video/mp4",
            "video/mpeg",
            "video/quicktime",
            "video/x-msvideo",
            # Archives (Zips, chat logs, etc.)
            "application/zip",
            "application/x-zip-compressed",
        ]
    )

    class Config:
        arbitrary_types_allowed = True


# Instantiate settings singleton
settings = Settings()

# Ensure directories exist
settings.STORAGE_DIR.mkdir(parents=True, exist_ok=True)
if settings.DATABASE_URL.startswith("sqlite:///"):
    db_path = Path(settings.DATABASE_URL.replace("sqlite:///", ""))
    db_path.parent.mkdir(parents=True, exist_ok=True)
