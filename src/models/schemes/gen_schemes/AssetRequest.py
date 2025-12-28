from pydantic import BaseModel
from typing import Optional


class AssetRequest(BaseModel):
    asset_id: str = None  # None make it opptional as well
    chunk_size: Optional[int] = 1000
    chunk_overlap: Optional[int] = 200
    do_reset: Optional[bool] = False
