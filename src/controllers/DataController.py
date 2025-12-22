from .BaseController import BaseController
from fastapi import UploadFile
from helpers.config import Settings
from models import ResponceMessagesEnum
from repositories import ProjectRepository, AssetRepository
from models.schemes.db_schemes import Asset
from models.enums import AssetTypesEnum
from .ProjectController import ProjectController
import re   
import os
import aiofiles

class DataController(BaseController):
    def __init__(self, app_setting: Settings):
        super().__init__(app_setting)
        self.size_scale = 1048576 # convert MB to Bytes

    def validate_uploaded_file(self, file: UploadFile):
        if file.content_type not in self.app_setting.FILE_ALLOWAED_TYPES:
            return False, ResponceMessagesEnum.FILE_TYPE_NOT_ALLOWED.value
        
        # Check size using seek/tell as UploadFile.size is not reliable
        file.file.seek(0, 2)
        file_size = file.file.tell()
        file.file.seek(0)
        
        if file_size > self.app_setting.FILE_MAX_SIZE * self.size_scale:
            return False, ResponceMessagesEnum.FILE_SIZE_TOO_LARGE.value
            
        return True, ResponceMessagesEnum.FILE_UPLOAD_SUCCESS.value

    def generate_unique_file_path(self, src_file_name: str, project_id: str):
        random_key = self.generate_random_string()
        project_path = ProjectController(app_setting=self.app_setting).get_project_path(project_id)
        clean_file_name = self.get_clean_file_name(src_file_name)
        
        new_file_name =  os.path.join(
            project_path, 
            random_key + "_" + clean_file_name)
        
        while os.path.exists(new_file_name):
            random_key = self.generate_random_string()
            new_file_name =  os.path.join(
                project_path, 
                random_key + "_" + clean_file_name)
        return new_file_name, random_key +"_" + clean_file_name
    
    def get_clean_file_name(self, src_file_name: str):
        #remove special characters except . and _ and convert to lower case
        clean_file_name = re.sub(r'[^\w.]', '', src_file_name.strip()).lower()
        #replace spaces with _
        clean_file_name = clean_file_name.replace(' ', '_')
        return clean_file_name

    async def handle_file_upload(self, project_title: str, file: UploadFile, db_client):
        # 1. Validate
        is_valid, message = self.validate_uploaded_file(file)
        if not is_valid:
             return False, message, None

        # 2. Get Project
        project_model = ProjectRepository(db_client, self.app_setting)
        project = await project_model.get_project_or_create_new(project_title)
        
        # 3. Generate Path
        file_path, asset_name = self.generate_unique_file_path(file.filename, project_title)
        
        # 4. Save File
        try:
            async with aiofiles.open(file_path, "wb") as out_file:
                 while chunk := await file.read(self.app_setting.FILE_CHUNK_SIZE):
                     await out_file.write(chunk)
        except Exception as e:
            return False, f"Error uploading file: {e}", None

        # 5. Create Asset
        asset_model = AssetRepository(db_client, self.app_setting)
        asset = Asset(
            asset_project_id=project.id,
            asset_type=AssetTypesEnum.FILE.value,
            asset_name=asset_name,
            asset_size=os.path.getsize(file_path),
            asset_path=file_path,
            asset_metadata={"file_path": file_path}
        )
        asset_record = await asset_model.create_asset(asset)
        
        return True, ResponceMessagesEnum.FILE_UPLOAD_SUCCESS.value, str(asset_record.id)
    