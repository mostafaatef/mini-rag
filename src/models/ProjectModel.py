from .BaseDataModel import BaseDataModel
from helpers.config import Settings
from .schemes.db_schemes.project import Project
from models.enums.DatabaseEnum import DatabaseEnum

class ProjectModel(BaseDataModel):
    def __init__(self, db_client: object, app_settings: Settings):
        super().__init__(db_client, app_settings)
        self.collection = self.db_client[DatabaseEnum.COLLECTION_PROJECTS_NAME]
    
    async def create_project(self, project: Project):
        result = await self.collection.insert_one(project.dict(by_alias=True, exclude_none=True))
        project.id = result.inserted_id
        return project

    async def get_project_or_create_new(self, project_id: str):
        record = await self.collection.find_one({"project_id": project_id})
        if record is None:
            new_project = Project(project_id=project_id)
            new_project = await self.create_project(new_project)
            return new_project
        return Project(**record)
    
    async def get_all_projects(self, page: int = 1, page_size: int = 10):
        total_records = await self.collection.count_documents({})
        total_pages = (total_records + page_size - 1) // page_size
        
        cursor = await self.collection.find().skip((page - 1) * page_size).limit(page_size)
        projects = []
        async for project_doc in cursor:
            projects.append(Project(**project_doc))
        return projects, total_pages