from .BaseRepository import BaseRepository
from typing import List
from src.helpers.config import Settings
from src.models.schemes.db_schemes.chunk import Chunk
from src.models.enums.DatabaseEnum import DatabaseEnum
from bson import ObjectId
from pymongo import InsertOne


class ChunkRepository(BaseRepository):
    def __init__(self, db_client: object, app_settings: Settings):
        super().__init__(db_client, app_settings)
        self.collection = self.db_client[DatabaseEnum.COLLECTION_CHUNKS_NAME]

    async def create_indexes(self):
        indexes = Chunk.get_indexes()
        for index in indexes:
            await self.collection.create_index(
                index["key"], name=index["name"], unique=index["unique"]
            )

    @classmethod
    async def init_indexes(cls, db_client: object):
        collection = db_client[DatabaseEnum.COLLECTION_CHUNKS_NAME]
        indexes = Chunk.get_indexes()
        for index in indexes:
            await collection.create_index(
                index["key"], name=index["name"], unique=index["unique"]
            )

    async def create_chunk(self, chunk: Chunk):
        result = await self.collection.insert_one(
            chunk.dict(by_alias=True, exclude_none=True)
        )
        chunk.id = result.inserted_id
        return chunk

    async def get_chunk_by_id(self, chunk_id: str):
        record = await self.collection.find_one({"_id": ObjectId(chunk_id)})
        if record is None:
            return None
        return Chunk(**record)

    async def insert_many_chunks(self, chunks: List[Chunk], batch_size: int = 100):
        for i in range(0, len(chunks), batch_size):
            batch = chunks[i : i + batch_size]
            operations = [
                InsertOne(chunk.dict(by_alias=True, exclude_none=True))
                for chunk in batch
            ]
            await self.collection.bulk_write(operations)
        return len(chunks)

    async def delete_chunks_by_project_id(self, project_id: str):
        result = await self.collection.delete_many(
            {"chunk_project_id": ObjectId(project_id)}
        )
        return result.deleted_count

    async def get_chunks_by_project_id(
        self, project_id: str, page_no: int = 1, page_size: int = 50
    ):
        cursor = self.collection.find(
            {"chunk_project_id": ObjectId(project_id)},
            skip=(page_no - 1) * page_size,
            limit=page_size,
        )
        chunks = []
        async for chunk_doc in cursor:
            chunks.append(Chunk(**chunk_doc))
        return chunks

    async def delete_chunks_by_file_id(self, file_id: str):
        result = await self.collection.delete_many(
            {"chunk_asset_id": ObjectId(file_id)}
        )
        return result.deleted_count

    async def insert_bulk(self, chunks: List[Chunk]):
        result = await self.collection.insert_many(
            [chunk.dict(by_alias=True, exclude_none=True) for chunk in chunks]
        )
        return result.inserted_ids
