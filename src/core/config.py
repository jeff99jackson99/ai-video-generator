"""Configuration management for AI Video Generator."""

import os
from pathlib import Path
from typing import Optional
from cryptography.fernet import Fernet
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class Config:
    """Application configuration."""

    # API Keys (optional, will use free alternatives if not provided)
    GEMINI_API_KEY: Optional[str] = os.getenv("GEMINI_API_KEY")
    GROQ_API_KEY: Optional[str] = os.getenv("GROQ_API_KEY")
    OPENAI_API_KEY: Optional[str] = os.getenv("OPENAI_API_KEY")

    # Media API Keys
    PEXELS_API_KEY: Optional[str] = os.getenv("PEXELS_API_KEY")
    UNSPLASH_API_KEY: Optional[str] = os.getenv("UNSPLASH_API_KEY")
    PIXABAY_API_KEY: Optional[str] = os.getenv("PIXABAY_API_KEY")

    # Application Settings
    APP_HOST: str = os.getenv("APP_HOST", "0.0.0.0")
    # Support both APP_PORT and PORT (for Railway, Heroku, etc.)
    APP_PORT: int = int(os.getenv("PORT", os.getenv("APP_PORT", "8000")))
    DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"

    # Storage
    DATA_DIR: Path = Path(os.getenv("DATA_DIR", "./data"))
    OUTPUT_DIR: Path = Path(os.getenv("OUTPUT_DIR", "./output"))
    MEDIA_DIR: Path = DATA_DIR / "media"
    VOICEOVER_DIR: Path = DATA_DIR / "voiceovers"
    MAX_VIDEO_LENGTH_SECONDS: int = int(os.getenv("MAX_VIDEO_LENGTH_SECONDS", "300"))

    # Job Processing
    MAX_CONCURRENT_JOBS: int = int(os.getenv("MAX_CONCURRENT_JOBS", "2"))
    JOB_TIMEOUT_SECONDS: int = int(os.getenv("JOB_TIMEOUT_SECONDS", "600"))

    # Security
    SECRET_KEY: str = os.getenv("SECRET_KEY", "dev_secret_key")

    @classmethod
    def ensure_directories(cls) -> None:
        """Create necessary directories if they don't exist."""
        cls.DATA_DIR.mkdir(exist_ok=True)
        cls.OUTPUT_DIR.mkdir(exist_ok=True)
        cls.MEDIA_DIR.mkdir(exist_ok=True)
        cls.VOICEOVER_DIR.mkdir(exist_ok=True)

    @classmethod
    def get_encryption_key(cls) -> bytes:
        """Get or generate encryption key for storing API keys."""
        key_file = cls.DATA_DIR / ".key"
        if key_file.exists():
            return key_file.read_bytes()
        else:
            key = Fernet.generate_key()
            cls.DATA_DIR.mkdir(exist_ok=True)
            key_file.write_bytes(key)
            return key

    @classmethod
    def encrypt_api_key(cls, api_key: str) -> str:
        """Encrypt an API key for secure storage."""
        cipher = Fernet(cls.get_encryption_key())
        return cipher.encrypt(api_key.encode()).decode()

    @classmethod
    def decrypt_api_key(cls, encrypted_key: str) -> str:
        """Decrypt an API key."""
        cipher = Fernet(cls.get_encryption_key())
        return cipher.decrypt(encrypted_key.encode()).decode()


# Initialize directories on import
Config.ensure_directories()
