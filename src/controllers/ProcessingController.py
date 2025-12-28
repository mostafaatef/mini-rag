from .BaseController import BaseController
from .ProjectController import ProjectController
from langchain_community.document_loaders import TextLoader
from langchain_community.document_loaders import PyMuPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from src.models.enums import ProcessingEnum

from fastapi import UploadFile
from src.helpers.config import Settings
from src.models import ResponseMessagesEnum
from src.repositories import ProjectRepository, ChunkRepository, AssetRepository
from src.models.schemes.db_schemes import Chunk
import os
import logging

logger = logging.getLogger(__name__)


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

        logger.debug(
            f"Processing file: {asset_id}, Path: {file_path}, Extension: {file_extension}"
        )

        if not os.path.exists(file_path):
            logger.error(f"File not found: {file_path}")
            return None

        if file_extension.lower() == ProcessingEnum.TXT.value:
            return TextLoader(file_path, encoding="utf-8")
        elif file_extension.lower() == ProcessingEnum.PDF.value:
            return PyMuPDFLoader(file_path)
        else:
            logger.warning(f"Unsupported file type: {file_extension}")
            # raise ValueError(f"Unsupported file type: {file_extension}")
            return None

    def get_asset_content(self, asset_name: str):
        loader = self.get_document_loader(asset_name)
        if loader is None:
            logger.error(f"Loader is None for asset: {asset_name}")
            return None
        return loader.load()

    def process_asset_content(
        self, asset_name: str, chunk_size: int, chunk_overlap: int
    ):
        file_content = self.get_asset_content(asset_name)
        if file_content is None:
            return None

        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=len,
            is_separator_regex=False,
        )

        file_content_texts = [record.page_content for record in file_content]

        file_content_metadata = [record.metadata for record in file_content]

        chunks = text_splitter.create_documents(
            file_content_texts, metadatas=file_content_metadata
        )

        return chunks

    async def handle_asset_processing(
        self,
        project_title: str,
        asset_id: str,
        chunk_size: int,
        chunk_overlap: int,
        do_reset: bool,
        db_client,
    ):
        # 1. Get Project
        project_model = ProjectRepository(db_client, self.app_setting)
        project = await project_model.get_project_or_create_new(project_title)

        # 2. Get Asset/Assets
        asset_records = []
        if asset_id is not None:
            asset_model = AssetRepository(db_client, self.app_setting)
            asset_record = await asset_model.get_asset_by_id(asset_id)
            if asset_record is None:
                return False, ResponseMessagesEnum.FILE_NOT_FOUND.value, None, 0, 0
            asset_records = [asset_record]
        else:
            asset_model = AssetRepository(db_client, self.app_setting)
            asset_records = await asset_model.get_assets_by_project_id(project.id)
            if asset_records is None or len(asset_records) == 0:
                return False, ResponseMessagesEnum.FILE_NOT_FOUND.value, None

        # 3. Process Content
        # We pass as asset_name (filename) / assets, because process_asset_content constructs path from it
        # 3. Process Content & 4. Create Chunks
        all_chunks_records = []
        no_files_processed = 0
        no_files_chunked = 0

        for asset_record in asset_records:
            no_files_processed += 1
            logger.debug(f"Processing asset record: {asset_record.asset_name}")
            file_chunks = self.process_asset_content(
                asset_record.asset_name, chunk_size, chunk_overlap
            )

            if file_chunks is None or len(file_chunks) == 0:
                logger.debug(
                    f"Warning: No chunks chunked from asset: {asset_record.asset_name} (Skipping)"
                )
                continue

            no_files_chunked += 1
            # Create Chunks for this file
            file_chunks_records = [
                Chunk(
                    chunk_project_id=project.id,
                    chunk_asset_id=asset_record.id,
                    chunk_content=chunk.page_content,
                    chunk_metadata=chunk.metadata,
                    chunk_order=i + 1,
                )
                for i, chunk in enumerate(file_chunks)
            ]
            all_chunks_records.extend(file_chunks_records)

        if len(all_chunks_records) == 0:
            return (
                False,
                ResponseMessagesEnum.FILE_PROCESSING_FAILED.value,
                None,
                no_files_processed,
                no_files_chunked,
            )

        chunk_model = ChunkRepository(db_client, self.app_setting)

        if do_reset:
            _ = await chunk_model.delete_chunks_by_project_id(project.id)

        no_chunks_inserted = await chunk_model.insert_many_chunks(all_chunks_records)

        return (
            True,
            ResponseMessagesEnum.FILE_PROCESSING_SUCCESS.value,
            no_chunks_inserted,
            no_files_processed,
            no_files_chunked,
        )
