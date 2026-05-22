from functools import lru_cache
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Configuración centralizada de la aplicación validada por Pydantic."""

    openai_api_key: str
    model_name: str = "gpt-4o-mini"
    chroma_db_path: str = "chroma_db_advanced"
    max_iterations: int = 5

    # Permitir carga desde archivo .env local en el directorio raíz del proyecto
    model_config = SettingsConfigDict(
        env_file=str(Path(__file__).resolve().parent / ".env"),
        env_file_encoding="utf-8",
        extra="ignore"
    )


@lru_cache
def get_settings() -> Settings:
    """Devuelve una instancia cacheada de Settings."""
    return Settings()
