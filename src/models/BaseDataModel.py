from helpers.config import Settings

class BaseDataModel:
    def __init__(self, db_client: object, app_settings: Settings):
        self.db_client = db_client
        self.app_settings = app_settings