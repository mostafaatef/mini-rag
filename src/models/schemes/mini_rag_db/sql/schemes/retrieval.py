from pydantic import BaseModel
from typing import Optional


class RetrievedChunkIndex(BaseModel):
    id: Optional[str] = None
    text: str
    score: float
    metadata: Optional[dict] = None
    payload: Optional[dict] = None
