from pydantic import BaseModel, Field, validator
from typing import Optional
from bson import ObjectId


class Chunk(BaseModel):
    # _id: Optional[ObjectId] = None
    id: Optional[ObjectId] = Field(None, alias="_id")
    chunk_content: str = Field(..., min_length=1, description="Chunk Content")
    chunk_metadata: dict
    chunk_order: int = Field(..., gt=0)
    chunk_project_id: ObjectId
    chunk_asset_id: ObjectId

    class Config:
        arbitrary_types_allowed = True

    @classmethod
    def get_indexes(cls):
        return [
            {
                "key": [("chunk_project_id", 1)],
                "name": "chunk_project_id_index_1",
                "unique": False,
            },
            {
                "key": [("chunk_project_id", 1), ("chunk_asset_id", 1)],
                "name": "chunk_project_id_chunk_asset_id_index_1",
                "unique": False,
            },
        ]


class RetrievedChunkIndex(BaseModel):
    text: str
    score: float
