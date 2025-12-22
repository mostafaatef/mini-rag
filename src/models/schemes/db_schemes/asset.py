from pydantic import BaseModel, Field
from typing import Optional
from bson import ObjectId
from datetime import datetime

class Asset(BaseModel):
    id: Optional[ObjectId] = Field(None, alias="_id")
    asset_project_id: ObjectId
    asset_type: str = Field(..., min_length=1, description="File Type")
    asset_name: str = Field(..., min_length=1, description="File Name")
    asset_size: int = Field(gt=0, default=None,description="File Size")
    asset_path: str = Field(default=None,description="File Path")
    asset_metadata: dict = Field(default=None,description="File Metadata")
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        arbitrary_types_allowed = True

    @classmethod
    def get_indexes(cls):
        return [
            {
                "key":[
                    ("asset_project_id", 1)
                ],
                "name": "asset_project_id_index_1",
                "unique": False
            },
            {
                "key":[
                    ("asset_project_id", 1),
                    ("asset_name", 1)
                ],
                "name": "asset_project_id_asset_name_index_1",
                "unique": True
            }
        ]