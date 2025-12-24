from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    APP_NAME: str
    APP_VERSION: str

    FILE_ALLOWAED_TYPES: List[str]
    FILE_MAX_SIZE: int
    FILE_CHUNK_SIZE: int

    MONGODB_URL: str
    MONGODB_DB: str

    GENERATION_BACKEND_LLM: str
    EMBEDDING_BACKEND_LLM: str

    OPENAI_API_KEY: str = None
    COHERE_API_KEY: str = None
    GOOGLE_API_KEY: str = None

    OPENAI_API_URL: str = None
    GENERATION_MODEL_ID: str = None
    EMBEDDING_MODEL_ID: str = None
    EMBEDDING_MODEL_SIZE: str = None
    INPUT_MAX_CHARACTERS: int = None
    GENERATION_MAX_OUTPUT_TOKENS: int = None
    GENERATION_TEMPERATURE: float = None


def get_settings():
    return Settings()
