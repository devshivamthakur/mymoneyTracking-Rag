from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path

class Settings(BaseSettings):
    CHUNK_SIZE: int = 500
    CHUNK_OVERLAP: int = 50
    TOP_K: int = 5
    TEMPERATURE: float = 0.7

    # JWT Token Related
    secret_key: str
    refresh_secret_key: str
    algorithm: str
    ACCESS_TOKEN_EXPIRE_MINUTES: str
    REFRESH_TOKEN_EXPIRE_MINUTES: str
    json_model: str
    chat_model: str
    base_url: str
    OPENROUTER_API_KEY: str


    # Pydantic v2 config
    model_config = SettingsConfigDict(
        env_file=str(Path(__file__).resolve().parent / ".env"),
        env_file_encoding="utf-8"
    )

settings = Settings()
