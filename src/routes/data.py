from fastapi import APIRouter, FastAPI, Depends, File, UploadFile, status
from fastapi.responses import JSONResponse
from models.enums.ResponceEnum import ResponceMessagesEnum
import os
from helpers.config import get_settings, Settings
from controllers import DataController
from controllers import ProjectController
import aiofiles
import logging

logger = logging.getLogger("uvicorn_error")

data_router = APIRouter(
    prefix="/api/v1/data",
    tags=["api-v1-data"],
    responses={404: {"description": "Not found"}}
    
)

@data_router.post("/upload/{project_id}")
async def upload_file(project_id: str, file: UploadFile = File(...), 
                        app_setting:Settings = Depends(get_settings)):
    data_controller = DataController(app_setting)
    is_valid, return_message = data_controller.validate_uploaded_file(file)
    if not is_valid:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "is_valid": is_valid,
                "message": return_message
            }
        )
    project_controller = ProjectController(app_setting)
    project_dir_path = project_controller.get_project_path(project_id=project_id)
    file_path, file_id = data_controller.generate_unique_file_path(file.filename, project_id)    

    try:
        async with aiofiles.open(file_path, "wb") as out_file:
            while chunk := await file.read(app_setting.FILE_CHUNK_SIZE):
                await out_file.write(chunk)
    except Exception as e:
        logger.error(f"Error uploading file: {e}")

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "is_valid": True,
            "message": ResponceMessagesEnum.FILE_UPLOAD_SUCCESS.value,
            "file_id": file_id
        }
    )
