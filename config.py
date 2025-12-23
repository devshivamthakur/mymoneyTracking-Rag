from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path

class Settings(BaseSettings):
    MODEL_NAME: str = "gpt-3.5-turbo"
    EMBEDDING_MODEL_NAME: str = "text-embedding-ada-002"
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
    QDRANT_URL: str
    QDRANT_API_KEY: str
    QDRANT_COLLECTION_NAME: str
    HUGGING_FACE_TOKEN:str
    CHAT_HF_MODEL: str
    JSON_HF_MODEL: str

    # Pydantic v2 config
    model_config = SettingsConfigDict(
        env_file=str(Path(__file__).resolve().parent / ".env"),
        env_file_encoding="utf-8"
    )

settings = Settings()
