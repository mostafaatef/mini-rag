from pydantic import BaseModel, Field, validator
from typing import Optional
from bson import ObjectId

class Project(BaseModel):
    _id: Optional[ObjectId] = None
    project_id: str = Field(..., min_length=1, max_length=1, description="Project ID")
    project_name: Optional[str] = None
    project_description: Optional[str] = None

    @validator("project_id")
    def validate_project_id(cls, v):
        #if v in cls._id:
        #    raise ValueError("Project ID must be unique")
        if not v.isalnum():
            raise ValueError("Project ID must be alphanumeric")
        return v
    
    class Config:
        arbitrary_types_allowed = True