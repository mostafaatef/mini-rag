from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    APP_NAME: str
    APP_VERSION: str
    OPENAI_API_KEY: str
    
    FILE_ALLOWAED_TYPES: List[str]
    FILE_MAX_SIZE: int
    FILE_CHUNK_SIZE: int

    MONGODB_URL: str 
    MONGODB_DB: str

    # Removed legacy class config

def get_settings():
    return Settings()   

