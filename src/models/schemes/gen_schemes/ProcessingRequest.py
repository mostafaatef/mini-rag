from pydantic import BaseModel
from typing import Optional

class ProcessingRequest(BaseModel):
    asset_id: str = None # None make it opptional as well
    chunk_size: Optional[int] = 100
    chunk_overlap: Optional[int] = 20
    do_reset: Optional[bool] = False
    