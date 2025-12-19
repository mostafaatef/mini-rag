from .BaseController import BaseController
from .ProjectController import ProjectController
from langchain_community.document_loaders import TextLoader
from langchain_community.document_loaders import PyMuPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from models.enums import ProcessingEnum

from fastapi import UploadFile
from helpers.config import Settings
from models import ResponceMessagesEnum
import os

class ProcessingController(BaseController):
    def __init__(self, project_id: str, app_setting: Settings):
        super().__init__(app_setting)   
        self.project_id = project_id
        self.project_path = ProjectController(app_setting).get_project_path(project_id)
    
    def get_file_extension(self, file_id: str):
        return file_id.split(".")[-1]
    
    def get_document_loader(self, file_id: str):
        file_extension = self.get_file_extension(file_id)
        file_path = os.path.join(self.project_path, file_id)
        if file_extension == ProcessingEnum.TXT.value:
            return TextLoader(file_path,encoding="utf-8")
        elif file_extension == ProcessingEnum.PDF.value:
            return PyMuPDFLoader(file_path)
        else:
           # raise ValueError(f"Unsupported file type: {file_extension}")
           return None

    def get_file_content(self, file_id: str):
        loader = self.get_document_loader(file_id)
        if loader is None:
            return None
        return loader.load()
    
    def process_file_content(self, file_id: str, chunk_size: str, chunk_overlap: str):
        file_content = self.get_file_content(file_id)
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
    
   