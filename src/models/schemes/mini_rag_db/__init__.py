from src.helpers.config import get_settings

app_settings = get_settings()

if app_settings.DATABASE_TYPE == "SQL":
    from .sql.schemes.project import Project
    from .sql.schemes.chunk import Chunk
    from .sql.schemes.asset import Asset
else:
    from .nosql import Project
    from .nosql import Chunk
    from .nosql import Asset

__all__ = [
    "Project",
    "Chunk",
    "Asset",
]
