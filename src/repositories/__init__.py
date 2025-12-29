from src.helpers.config import get_settings

app_settings = get_settings()

if app_settings.DATABASE_TYPE == "SQL":
    from .sql.BaseRepository import BaseRepository
    from .sql.ProjectRepository import ProjectRepository
    from .sql.ChunkRepository import ChunkRepository
    from .sql.AssetRepository import AssetRepository
else:
    from .nosql.BaseRepository import BaseRepository
    from .nosql.ProjectRepository import ProjectRepository
    from .nosql.ChunkRepository import ChunkRepository
    from .nosql.AssetRepository import AssetRepository

__all__ = [
    "BaseRepository",
    "ProjectRepository",
    "ChunkRepository",
    "AssetRepository",
]
