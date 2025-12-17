from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    APP_NAME: str
    APP_VERSION: str
    OPENAI_API_KEY: str
    FILE_ALLOWAED_TYPES: list[str] = ["text/plain", "application/pdf"]
    FILE_MAX_SIZE: int = 10
    FILE_CHUNK_SIZE: int = 1000

    # Removed legacy class config

def get_settings():
    return Settings()   

