from pydantic import BaseModel, Field, validator
from typing import Optional
from bson import ObjectId

class Chunk(BaseModel):
    # _id: Optional[ObjectId] = None
    id: Optional[ObjectId] = Field(None, alias="_id")
    chunk_content: str = Field(..., min_length=1, description="Chunk Content")
    chunk_metadata: dict
    chunk_order: int = Field(..., gt=0)
    project_id: ObjectId
    file_id: str 

    class Config:
        arbitrary_types_allowed = True