from src.helpers.config import Settings
from sqlalchemy.ext.asyncio import AsyncSession


class BaseRepository:
    def __init__(self, db_client: AsyncSession, app_settings: Settings):
        self.session = db_client
        self.app_settings = app_settings
