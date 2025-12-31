from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List, Optional


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    APP_NAME: str
    APP_VERSION: str

    FILE_ALLOWED_TYPES: List[str]
    FILE_MAX_SIZE: int
    FILE_CHUNK_SIZE: int

    DATABASE_TYPE: str = "SQL"

    MONGODB_URL: str
    MONGODB_DB: str

    POSTGRES_USERNAME: str
    POSTGRES_PASSWORD: str
    POSTGRES_HOST: str
    POSTGRES_PORT: int
    POSTGRES_MAIN_DATABASE: str

    GENERATION_BACKEND_LLM: str
    EMBEDDING_BACKEND_LLM: str

    OPENAI_API_KEY: Optional[str] = None
    COHERE_API_KEY: Optional[str] = None
    GOOGLE_API_KEY: Optional[str] = None
    OLLAMA_BASE_URL: Optional[str] = None

    OPENAI_API_URL: Optional[str] = None
    GENERATION_MODEL_ID: Optional[str] = None
    EMBEDDING_MODEL_ID: Optional[str] = None
    EMBEDDING_MODEL_SIZE: Optional[str] = None
    INPUT_MAX_CHARACTERS: Optional[int] = None
    GENERATION_MAX_OUTPUT_TOKENS: Optional[int] = None
    GENERATION_TEMPERATURE: Optional[float] = None

    VECTOR_DB_BACKEND: str
    VECTOR_QDRANT_DB_PATH: str
    VECTOR_POSTGRES_DB_URL: str
    VECTOR_DB_DISTANCE_METHOD: Optional[str] = None
    VECTOR_POSTGRES_INDEX_CREATION_THRESHOLD: Optional[int] = 1000
    DEFAULT_LANG: str = "en"

    VECTOR_DB_BACKEND_LITERAL: List[str]
    EMBEDDING_BACKEND_LLM_LITERAL: List[str]
    GENERATION_BACKEND_LLM_LITERAL: List[str]
    DATABASE_TYPE_LITERAL: List[str]


def get_settings():
    return Settings()
