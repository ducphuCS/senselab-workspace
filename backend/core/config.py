"""Global backend configuration settings."""

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    app_name: str = "Compusense Sensory Lab"
    app_version: str = "0.1.0"
    database_url: str = os.getenv(
        "DATABASE_URL", "sqlite:///./compusense.db"
    )
    secret_key: str = os.getenv("SECRET_KEY", "compusense-insecure-secret-key")


settings = Settings()
