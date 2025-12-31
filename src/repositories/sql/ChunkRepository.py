from .BaseRepository import BaseRepository
from src.helpers.config import Settings
from src.models.schemes.mini_rag_db.sql.schemes.chunk import Chunk
from sqlalchemy import select, delete, func
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List


class ChunkRepository(BaseRepository):
    def __init__(self, db_client: AsyncSession, app_settings: Settings):
        super().__init__(db_client, app_settings)

    @classmethod
    async def init_indexes(cls, db_client: object):
        pass

    async def create_indexes(self):
        pass

    async def create_chunk(self, chunk: Chunk):
        self.session.add(chunk)
        await self.session.flush()
        await self.session.refresh(chunk)
        return chunk

    async def get_chunk_by_id(self, chunk_id: int):
        result = await self.session.execute(
            select(Chunk).where(Chunk.id == int(chunk_id))
        )
        return result.scalars().first()

    async def insert_many_chunks(self, chunks: List[Chunk], batch_size: int = 100):
        # We assume chunks are list of SQLA objects
        # SQLAlchemy add_all handles list of objects.
        # We can implement batching if memory is a concern, but for lists usually add_all is fine
        # followed by flush/commit logic outside or here.
        # The NoSQL implementation implies this method commits/writes.

        # We'll batch it to be safe and mimic the logic
        for i in range(0, len(chunks), batch_size):
            batch = chunks[i : i + batch_size]
            self.session.add_all(batch)
            await self.session.flush()  # Flush to send to DB

        return len(chunks)

    async def delete_chunks_by_project_id(self, project_id: int):
        query = delete(Chunk).where(Chunk.chunk_project_id == int(project_id))
        result = await self.session.execute(query)
        return result.rowcount

    async def get_chunks_by_project_id(
        self, project_id: int, page_no: int = 1, page_size: int = 50
    ):
        query = (
            select(Chunk)
            .where(Chunk.chunk_project_id == int(project_id))
            .limit(page_size)
            .offset((page_no - 1) * page_size)
        )

        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def delete_chunks_by_file_id(self, file_id: int):
        query = delete(Chunk).where(Chunk.chunk_asset_id == int(file_id))
        result = await self.session.execute(query)
        return result.rowcount

    async def insert_bulk(self, chunks: List[Chunk]):
        # Similar to insert_many_chunks but returns IDs?
        # In SQLA, after flush, IDs are populated on the instances.
        self.session.add_all(chunks)
        await self.session.flush()
        return [chunk.id for chunk in chunks]

    async def get_total_chunks_count(self, project_id: int):
        result = 0
        query = select(func.count(Chunk.id)).where(
            Chunk.chunk_project_id == int(project_id)
        )
        result = await self.session.execute(query)
        return result.scalar()
