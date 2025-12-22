from fastapi import APIRouter, FastAPI, Depends, File, UploadFile, status, Request
from fastapi.responses import JSONResponse
import aiofiles
import logging
import os
from models.schemes.RequestProcessor import RequestProcessor
from models import ProjectModel, ChunkModel, AssetModel
from models.schemes.db_schemes import Chunk, Asset
from models.enums import ResponceMessagesEnum,AssetTypesEnum
from helpers.config import get_settings, Settings
from controllers import DataController, ProjectController, ProcessingController    

logger = logging.getLogger("uvicorn_error")

data_router = APIRouter(
    prefix="/api/v1/data",
    tags=["api-v1-data"],
    responses={404: {"description": "Not found"}}
    
)

@data_router.post("/upload/{project_title}")
async def upload_file(request: Request, project_title: str, file: UploadFile = File(...), 
                        app_setting:Settings = Depends(get_settings)):
    
    project_model = await ProjectModel.create_instance(request.app.mongodb_db_client, app_setting)
    project = await project_model.get_project_or_create_new(project_title)
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
    #project_controller = ProjectController(app_setting)
    #project_dir_path = project_controller.get_project_path(project_id=project.id)
    file_path, file_id = data_controller.generate_unique_file_path(file.filename, project_title)    

    try:
        async with aiofiles.open(file_path, "wb") as out_file:
            while chunk := await file.read(app_setting.FILE_CHUNK_SIZE):
                await out_file.write(chunk)
    except Exception as e:
        logger.error(f"Error uploading file: {e}")  

    #save asset in DB
    asset_model = await AssetModel.create_instance(request.app.mongodb_db_client, app_setting)
    asset = Asset(
        asset_project_id=project.id,
        asset_type=AssetTypesEnum.FILE.value,
        asset_name=file_id,
        asset_size=os.path.getsize(file_path),  
        asset_path=file_path,
        asset_metadata={"file_path": file_path}
    )
    asset_record = await asset_model.create_asset(asset)

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "is_valid": True,
            "message": ResponceMessagesEnum.FILE_UPLOAD_SUCCESS.value,
            "file_id": str(asset_record.id),
        }
    )
@data_router.post("/process/{project_title}")
async def process_file(request: Request, project_title: str, request_processor: RequestProcessor, 
                        app_setting:Settings = Depends(get_settings)):
    
    file_id = request_processor.file_id
    chunk_size = request_processor.chunk_size
    chunk_overlap = request_processor.chunk_overlap
    do_reset = request_processor.do_reset
    
    request_controller = ProcessingController(project_title, app_setting)
    project_model = await ProjectModel.create_instance(request.app.mongodb_db_client, app_setting)
    project = await project_model.get_project_or_create_new(project_title)
    
    asset_model = await AssetModel.create_instance(request.app.mongodb_db_client, app_setting)
    asset_record = await asset_model.get_asset_by_id(file_id)
    if asset_record is None:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "is_valid": False,
                "message": ResponceMessagesEnum.FILE_NOT_FOUND.value
            }
        )
    
    chunk_model = await ChunkModel.create_instance(request.app.mongodb_db_client, app_setting)

    file_chunks = request_controller.process_file_content(asset_record.asset_name, chunk_size, chunk_overlap)
    if file_chunks is None or len(file_chunks) == 0:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "is_valid": False,
                "message": ResponceMessagesEnum.FILE_PROCESSING_FAILED.value
            }
        )
    
    file_chunks_records = [
        Chunk(
            chunk_project_id=project.id,
            chunk_file_id=file_id,
            chunk_content=chunk.page_content,
            chunk_metadata=chunk.metadata,
            chunk_order=i+1
        )
        for i, chunk in enumerate(file_chunks)
    ]
    
    if do_reset:
       _ = await chunk_model.delete_chunks_by_project_id(project.id)
    
    no_chunks_inserted = await chunk_model.insert_many_chunks(file_chunks_records)
    
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "is_valid": True,
            "message": ResponceMessagesEnum.FILE_PROCESSING_SUCCESS.value,
            "chunks_inserted_no": no_chunks_inserted
        }
    )