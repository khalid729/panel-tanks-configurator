"""
Application Configuration
"""
from pathlib import Path
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings"""
    APP_NAME: str = "GRP Panel Tank Configuration API"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True

    # Data files path (inside app/data folder)
    DATA_DIR: Path = Path(__file__).parent.parent / "data"

    # Exchange rate (USD to SAR)
    DEFAULT_EXCHANGE_RATE: float = 3.75

    # API settings
    API_V1_PREFIX: str = "/api/v1"

    class Config:
        env_file = ".env"


settings = Settings()
