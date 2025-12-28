from pydantic import BaseModel
from typing import Optional


class PushRequest(BaseModel):
    do_reset: Optional[bool] = False


class SearchRequest(BaseModel):
    query: str
    limit: Optional[int] = 3
