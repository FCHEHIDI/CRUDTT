"""Configuration centralisée via pydantic-settings."""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Paramètres de l'application chargés depuis .env.

    Attributes:
        APP_NAME: Nom de l'application.
        APP_ENV: Environnement (development, staging, production).
        DEBUG: Mode debug.
        DATABASE_URL: URL de connexion à la base de données.
        CORS_ORIGINS: Liste des origines CORS autorisées.
    """

    APP_NAME: str = "Internal Tools API"
    APP_ENV: str = "development"
    DEBUG: bool = True
    DATABASE_URL: str = "sqlite:///./dev.db"
    CORS_ORIGINS: list[str] = ["http://localhost:3000"]

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()
