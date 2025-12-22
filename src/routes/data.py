from fastapi import APIRouter, Depends, File, UploadFile, status, Request
from fastapi.responses import JSONResponse
from models.schemes.gen_schemes.ProcessingRequest import ProcessingRequest
from helpers.config import get_settings, Settings
from controllers import DataController, ProcessingController    

data_router = APIRouter(
    prefix="/api/v1/data",
    tags=["api-v1-data"],
    responses={404: {"description": "Not found"}}
)

@data_router.post("/upload/{project_title}")
async def upload_file(request: Request, project_title: str, file: UploadFile = File(...), 
                        app_setting:Settings = Depends(get_settings)):
    
    data_controller = DataController(app_setting)
    is_valid, message, asset_id = await data_controller.handle_file_upload(project_title, file, request.app.mongodb_db_client)

    if not is_valid:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "is_valid": is_valid,
                "message": message
            }
        )
    
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "is_valid": True,
            "message": message,
            "asset_id": asset_id,
        }
    )

@data_router.post("/process/{project_title}")
async def process_file(request: Request, project_title: str, processing_request: ProcessingRequest, 
                        app_setting:Settings = Depends(get_settings)):
    
    asset_id = processing_request.asset_id
    chunk_size = processing_request.chunk_size
    chunk_overlap = processing_request.chunk_overlap
    do_reset = processing_request   .do_reset
    
    request_controller = ProcessingController(project_title, app_setting)
    is_valid, message, no_chunks_inserted, no_files_processed, no_files_chunked = await request_controller.handle_asset_processing(
        project_title, asset_id, chunk_size, chunk_overlap, do_reset, request.app.mongodb_db_client
    )

    if not is_valid:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "is_valid": is_valid,
                "message": message
            }
        )
    
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "is_valid": True,
            "message": message,
            "chunks_inserted_no": no_chunks_inserted,
            "no_files_processed": no_files_processed,
            "no_files_chunked": no_files_chunked
        }
    )