from .VectorDBInterface import VectorDBInterface
from .VectorDBEnums import VectorDBEnum, DistanceMethodEnum
from .providers.QdrantVDBProvider import QdrantVDBProvider
from .providers.PGVectorProvider import PGVectorProvider
from .providers.BaseVDBProvider import BaseVectorDBProvider
from src.helpers.config import Settings


class VectorDBProviderFactory:
    def __init__(self, settings: Settings):
        self.settings = settings
        self.base_vdb_provider = BaseVectorDBProvider(
            db_path=self.settings.VECTOR_DB_PATH,
            distance_method=DistanceMethodEnum(self.settings.VECTOR_DB_DISTANCE_METHOD),
        )

    def create_provider(self, vector_db_type: VectorDBEnum) -> VectorDBInterface:
        db_path = self.base_vdb_provider.get_database_dir(self.settings.VECTOR_DB_PATH)
        if vector_db_type == VectorDBEnum.QDRANT.value:
            return QdrantVDBProvider(
                db_path=db_path,
                distance_method=DistanceMethodEnum(
                    self.settings.VECTOR_DB_DISTANCE_METHOD
                ),
            )
        elif vector_db_type == VectorDBEnum.PGVECTOR.value:
            return PGVectorProvider(
                db_url=self.settings.VECTOR_DB_URL,
                distance_method=DistanceMethodEnum(
                    self.settings.VECTOR_DB_DISTANCE_METHOD
                ),
            )
        else:
            raise ValueError(f"Unknown vector db type: {vector_db_type}")
