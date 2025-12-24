from src.helpers.config import get_settings, Settings
from fastapi import Depends
import os
import uuid
import random
import string


class BaseController:
    def __init__(self, app_setting: Settings):
        self.app_setting = app_setting
        self.base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.files_dir = os.path.join(self.base_dir, "assets/files")

    def generate_random_string(self, length: int = 12):
        return "".join(random.choices(string.ascii_letters + string.digits, k=length))
