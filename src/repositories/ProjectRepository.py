from .BaseRepository import BaseRepository
from src.helpers.config import Settings
from src.models.schemes.db_schemes.project import Project
from src.models.enums.DatabaseEnum import DatabaseEnum

class ProjectRepository(BaseRepository):
    def __init__(self, db_client: object, app_settings: Settings):
        super().__init__(db_client, app_settings)
        self.collection = self.db_client[DatabaseEnum.COLLECTION_PROJECTS_NAME]
    
    async def create_indexes(self):
        indexes = Project.get_indexes()
        for index in indexes:
            await self.collection.create_index(
                index["key"],
                name=index["name"],
                unique=index["unique"]
            )

    @classmethod
    async def init_indexes(cls, db_client: object):
        collection = db_client[DatabaseEnum.COLLECTION_PROJECTS_NAME]
        indexes = Project.get_indexes()
        for index in indexes:
            await collection.create_index(
                index["key"],
                name=index["name"],
                unique=index["unique"]
            )
    
    async def create_indexes(self):
        indexes = Project.get_indexes()
        for index in indexes:
            await self.collection.create_index(
                index["key"],
                name=index["name"],
                unique=index["unique"]
            )
    
    async def create_project(self, project: Project):
        result = await self.collection.insert_one(project.dict(by_alias=True, exclude_none=True))
        project.id = result.inserted_id
        return project

    async def get_project_or_create_new(self, project_title: str):
        record = await self.collection.find_one({"project_title": project_title})
        if record is None:
            new_project = Project(project_title=project_title)
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