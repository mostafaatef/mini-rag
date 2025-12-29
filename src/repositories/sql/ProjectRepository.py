from .BaseRepository import BaseRepository
from src.helpers.config import Settings
from src.models.schemes.mini_rag_db.sql.schemes.project import Project
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession


class ProjectRepository(BaseRepository):
    def __init__(self, db_client: AsyncSession, app_settings: Settings):
        super().__init__(db_client, app_settings)

    @classmethod
    async def init_indexes(cls, db_client: object):
        # In SQL, indexes are typically managed by Alembic migrations,
        # but if we needed to do something here, we could.
        pass

    async def create_project(self, project: Project):
        self.session.add(project)
        await self.session.flush()
        await self.session.refresh(project)
        return project

    async def get_project_or_create_new(self, project_title: str):
        result = await self.session.execute(
            select(Project).where(Project.title == project_title)
        )
        record = result.scalars().first()

        if record is None:
            new_project = Project(title=project_title)
            new_project = await self.create_project(new_project)
            return new_project
        return record

    async def get_all_projects(self, page: int = 1, page_size: int = 10):
        # Count total records
        count_query = select(func.count()).select_from(Project)
        count_result = await self.session.execute(count_query)
        total_records = count_result.scalar_one()

        total_pages = (total_records + page_size - 1) // page_size

        # Get page records
        query = select(Project).limit(page_size).offset((page - 1) * page_size)
        result = await self.session.execute(query)
        projects = result.scalars().all()

        return list(projects), total_pages
