from pydantic import BaseModel, Field, validator
from typing import Optional
from bson import ObjectId

class Project(BaseModel):
    # _id: Optional[ObjectId] = None
    id: Optional[ObjectId] = Field(None, alias="_id")
    project_id: str = Field(..., min_length=1, max_length=50, description="Project ID")
    project_name: Optional[str] = None
    project_description: Optional[str] = None

    @validator("project_id")
    def validate_project_id(cls, v):
        #if v in cls._id:
        #    raise ValueError("Project ID must be unique")
        if not v.replace('_', '').isalnum():
            raise ValueError("Project ID must be alphanumeric and underscores")
        return v
    
    class Config:
        arbitrary_types_allowed = True