from typing import Optional
from ..VectorDBInterface import VectorDBInterface
from ..VectorDBEnums import VectorDBEnum, DistanceMethodEnum
from logging import getLogger
from typing import List
import os


class BaseVectorDBProvider(VectorDBInterface):
    def __init__(self, db_path: str, distance_method: DistanceMethodEnum):
        self.db_path = db_path
        self.distance_method = distance_method
        self.client = None
        self.base_dir = os.path.dirname(
            os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        )
        self.database_dir = os.path.join(self.base_dir, "assets/database")
        self.logger = getLogger(__name__)
        self.logger.info("BaseVectorDBProvider initialized")

    def get_database_dir(self, db_name: str):
        target_dir = os.path.join(self.database_dir, db_name)
        if not os.path.exists(target_dir):
            os.makedirs(target_dir)
        return target_dir

    def connect(self):
        pass

    def disconnect(self):
        pass

    def list_all_collections(self) -> list:
        pass

    def create_collection(
        self, collection_name: str, embedding_size: int, do_reset: bool = False
    ):
        pass

    def is_collection_exists(self, collection_name: str) -> bool:
        pass

    def get_collection_info(self, collection_name: str) -> dict:
        pass

    def delete_collection(self, collection_name: str):
        pass

    def insert_one(
        self,
        collection_name: str,
        texts: str,
        vector: List[float],
        metadatas: Optional[dict] = None,
        record_id: Optional[str] = None,
    ):
        pass

    def insert_many(
        self,
        collection_name: str,
        texts: List[str],
        metadatas: Optional[List[dict]] = None,
        vector: Optional[List[float]] = None,
        record_id: Optional[List[str]] = None,
        batch_size: Optional[int] = 100,
    ):
        pass

    def search_by_vector(
        self,
        collection_name: str,
        vector: List[float],
        metadatas: Optional[List[dict]] = None,
        limit: Optional[int] = 10,
    ):
        pass
