from .VectorDBInterface import VectorDBInterface
from .VectorDBEnums import VectorDBEnum
from .providers.QdrantVDBProvider import QdrantVDBProvider
from .providers.PGVectorProvider import PGVectorProvider
from .providers.BaseVDBProvider import BaseVectorDBProvider
from src.helpers.config import Settings
from typing import Any


class VectorDBProviderFactory:
    def __init__(self, settings: Settings):
        self.settings = settings
        # Base provider needs a path for local DBs (like Qdrant local).
        # We use VECTOR_QDRANT_DB_PATH as the default for BaseVDBProvider's helper methods.
        qdrant_path = getattr(self.settings, "VECTOR_QDRANT_DB_PATH", "qdrant_db")
        self.base_vdb_provider = BaseVectorDBProvider(
            db_path=qdrant_path,
            distance_method=self.settings.VECTOR_DB_DISTANCE_METHOD,
        )

    def create_provider(
        self, vector_db_type: str, db_client: Any = None
    ) -> VectorDBInterface:
        if vector_db_type == VectorDBEnum.QDRANT.value:
            qdrant_path = getattr(self.settings, "VECTOR_QDRANT_DB_PATH", "qdrant_db")
            qdrant_db_client = self.base_vdb_provider.get_database_dir(qdrant_path)
            return QdrantVDBProvider(
                db_client=qdrant_db_client,
                distance_method=self.settings.VECTOR_DB_DISTANCE_METHOD,
                index_threshold=getattr(
                    self.settings, "VECTOR_POSTGRES_INDEX_CREATION_THRESHOLD", 1000
                ),
            )
        elif vector_db_type == VectorDBEnum.PGVECTOR.value:
            return PGVectorProvider(
                db_client=db_client,
                distance_method=self.settings.VECTOR_DB_DISTANCE_METHOD,
                index_threshold=getattr(
                    self.settings, "VECTOR_POSTGRES_INDEX_CREATION_THRESHOLD", 1000
                ),
            )
        else:
            raise ValueError(f"Unknown vector db type: {vector_db_type}")
