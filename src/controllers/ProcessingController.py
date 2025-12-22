from .BaseController import BaseController
from .ProjectController import ProjectController
from langchain_community.document_loaders import TextLoader
from langchain_community.document_loaders import PyMuPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from models.enums import ProcessingEnum

from fastapi import UploadFile
from helpers.config import Settings
from models import ResponceMessagesEnum, ProjectModel, ChunkModel, AssetModel
from models.schemes.db_schemes import Chunk
import os

class ProcessingController(BaseController):
    def __init__(self, project_id: str, app_setting: Settings):
        super().__init__(app_setting)   
        self.project_id = project_id
        self.project_path = ProjectController(app_setting).get_project_path(project_id)
    
    def get_asset_extension(self, asset_id: str):
        return asset_id.split(".")[-1]
    
    def get_document_loader(self, asset_id: str):
        file_extension = self.get_asset_extension(asset_id)
        file_path = os.path.join(self.project_path, asset_id)
        if file_extension == ProcessingEnum.TXT.value:
            return TextLoader(file_path,encoding="utf-8")
        elif file_extension == ProcessingEnum.PDF.value:
            return PyMuPDFLoader(file_path)
        else:
           # raise ValueError(f"Unsupported file type: {file_extension}")
           return None

    def get_asset_content(self, asset_id: str):
        loader = self.get_document_loader(asset_id)
        if loader is None:
            return None
        return loader.load()
    
    def process_asset_content(self, asset_id: str, chunk_size: int, chunk_overlap: int):
        file_content = self.get_asset_content(asset_id)
        if file_content is None:
            return None
        
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size = chunk_size,
            chunk_overlap = chunk_overlap,
            length_function = len,
            is_separator_regex = False
        )

        file_content_texts =[
            record.page_content
            for record in file_content
        ]

        file_content_metadata =[
            record.metadata
            for record in file_content
        ]

        chuncks = text_splitter.create_documents(
            file_content_texts,
            metadatas= file_content_metadata

        )

        return chuncks

    async def handle_asset_processing(self, project_title: str, asset_id: str, chunk_size: int, chunk_overlap: int, do_reset: bool, db_client):
        # 1. Get Project
        project_model = ProjectModel(db_client, self.app_setting)
        project = await project_model.get_project_or_create_new(project_title)
        
        # 2. Get Asset
        asset_model = AssetModel(db_client, self.app_setting)
        asset_record = await asset_model.get_asset_by_id(asset_id)
        if asset_record is None:
            return False, ResponceMessagesEnum.FILE_NOT_FOUND.value, None
        
        # 3. Process Content
        # We pass as asset_name (filename) because process_asset_content constructs path from it
        file_chunks = self.process_asset_content(asset_record.asset_name, chunk_size, chunk_overlap)
        
        if file_chunks is None or len(file_chunks) == 0:
            return False, ResponceMessagesEnum.FILE_PROCESSING_FAILED.value, None

        # 4. Create Chunks
        file_chunks_records = [
            Chunk(
                chunk_project_id=project.id,
                chunk_asset_id=asset_id,
                chunk_content=chunk.page_content,
                chunk_metadata=chunk.metadata,
                chunk_order=i+1
            )
            for i, chunk in enumerate(file_chunks)
        ]
        
        chunk_model = ChunkModel(db_client, self.app_setting)
        
        if do_reset:
           _ = await chunk_model.delete_chunks_by_project_id(project.id)
        
        no_chunks_inserted = await chunk_model.insert_many_chunks(file_chunks_records)
        
        return True, ResponceMessagesEnum.FILE_PROCESSING_SUCCESS.value, no_chunks_inserted
    
   