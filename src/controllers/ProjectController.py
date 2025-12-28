from .BaseController import BaseController
from fastapi import UploadFile
from src.helpers.config import Settings
from src.models import ResponseMessagesEnum
import os


class ProjectController(BaseController):
    def __init__(self, app_setting: Settings):
        super().__init__(app_setting)

    def get_project_path(self, project_id: str):
        project_dir = os.path.join(self.files_dir, project_id)
        if not os.path.exists(project_dir):
            os.makedirs(project_dir)
        return project_dir
