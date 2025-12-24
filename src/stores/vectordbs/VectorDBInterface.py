from abc import ABC, abstractmethod
from typing import List, Optional


class VectorDBInterface(ABC):
    @abstractmethod
    def connect(self):
        pass

    @abstractmethod
    def disconnect(self):
        pass

    @abstractmethod
    def list_all_collections(self) -> list:
        pass

    @abstractmethod
    def create_collection(
        self, collection_name: str, embedding_size: int, do_reset: bool = False
    ) -> bool:
        pass

    @abstractmethod
    def is_collection_exists(self, collection_name: str) -> bool:
        pass

    @abstractmethod
    def get_collection_info(self, collection_name: str) -> dict:
        pass

    @abstractmethod
    def delete_collection(self, collection_name: str):
        pass

    @abstractmethod
    def insert_one(
        self,
        collection_name: str,
        text: str,
        vector: List[float],
        metadatas: Optional[dict] = None,
        record_id: Optional[str] = None,
    ):
        pass

    @abstractmethod
    def insert_many(
        self,
        collection_name: str,
        texts: List[str],
        metadatas: Optional[List[dict]] = None,
        vectors: Optional[List[List[float]]] = None,
        record_ids: Optional[List[str]] = None,
        batch_size: Optional[int] = 100,
    ):
        pass

    @abstractmethod
    def search_by_vector(
        self,
        collection_name: str,
        vector: List[float],
        metadatas: Optional[List[dict]] = None,
        limit: Optional[int] = 10,
    ):
        pass
