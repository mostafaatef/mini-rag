from pydantic import BaseModel, Field, validator
from typing import Optional
from bson import ObjectId

class Chunk(BaseModel):
    _id: Optional[ObjectId] = None
    chunk_text: str = Field(..., min_length=1, description="Chunk Text")
    chunk_metadata: dict
    chunk_order: int = Field(..., gt=0)
    chunk_project_id: ObjectId 

    class Config:
        arbitrary_types_allowed = True