from qdrant_client import QdrantClient, models
from qdrant_client.http.models import Distance
import uuid
from ..VectorDBInterface import VectorDBInterface
from logging import getLogger
from typing import List, Optional

from .BaseVDBProvider import BaseVectorDBProvider
from ..VectorDBEnums import VectorDBEnum, DistanceMethodEnum


class QdrantVDB(BaseVectorDBProvider):
    def __init__(self, db_path: str, distance_method: DistanceMethodEnum):
        super().__init__(db_path, distance_method)
        self.distance_method = None

        if distance_method == DistanceMethodEnum.L2:
            self.distance_method = Distance.L2
        elif distance_method == DistanceMethodEnum.IP:
            self.distance_method = Distance.IP
        elif distance_method == DistanceMethodEnum.COSINE:
            self.distance_method = models.Distance.COSINE
        elif distance_method == DistanceMethodEnum.DOT:
            self.distance_method = models.Distance.DOT

        self.logger.info("QdrantVDB initialized")

    def connect(self):
        self.client = QdrantClient(path=self.db_path, distance=self.distance_method)
        self.logger.info("QdrantVDB connected")

    def disconnect(self):
        if self.client:
            self.client.close()

    def is_collection_exists(self, collection_name: str) -> bool:
        return self.client.collection_exists(collection_name)

    def list_all_collections(self) -> list:
        return self.client.get_collections()

    def get_collection_info(self, collection_name: str) -> dict:
        return self.client.get_collection(collection_name)

    def delete_collection(self, collection_name: str):
        if self.is_collection_exists(collection_name):
            self.client.delete_collection(collection_name)

    def create_collection(
        self, collection_name: str, embedding_size: int, do_reset: bool = False
    ):
        if self.is_collection_exists(collection_name):
            if do_reset:
                self.delete_collection(collection_name)
            else:
                self.logger.error(f"Collection {collection_name} already exists")
                return False
        self.client.create_collection(
            collection_name=collection_name,
            vectors_config=models.VectorParams(
                size=embedding_size,
                distance=self.distance_method,
            ),
        )
        return True

    def insert_one(
        self,
        collection_name: str,
        text: str,
        vector: List[float],
        metadatas: Optional[dict] = None,
        record_id: Optional[str] = None,
    ):
        if not self.is_collection_exists(collection_name):
            self.logger.error(f"Collection {collection_name} does not exist")
            return False

        record_id = record_id if record_id else str(uuid.uuid4())

        self.client.upload_records(
            collection_name=collection_name,
            records=[
                models.Record(
                    id=record_id,
                    vector=vector,
                    payload={
                        "text": text,
                        "metadata": metadatas,
                    },
                )
            ],
        )
        return True

    def insert_many(
        self,
        collection_name: str,
        texts: List[str],
        metadatas: Optional[List[dict]] = None,
        vectors: Optional[List[List[float]]] = None,
        record_ids: Optional[List[str]] = None,
        batch_size: Optional[int] = 100,
    ):
        if not self.is_collection_exists(collection_name):
            self.logger.error(f"Collection {collection_name} does not exist")
            return False
        if metadatas is None:
            metadatas = [None] * len(texts)
        if vectors is None:
            vectors = [None] * len(texts)
        if record_ids is None:
            record_ids = [str(uuid.uuid4()) for _ in range(len(texts))]

        for i in range(0, len(texts), batch_size):
            batch_end = min(i + batch_size, len(texts))
            batch_texts = texts[i:batch_end]
            batch_metadatas = metadatas[i:batch_end]
            batch_vectors = vectors[i:batch_end]
            batch_record_ids = record_ids[i:batch_end]

            batch_records = []
            for j in range(len(batch_texts)):
                batch_records.append(
                    models.Record(
                        id=batch_record_ids[j],
                        vector=batch_vectors[j],
                        payload={
                            "text": batch_texts[j],
                            "metadata": batch_metadatas[j],
                        },
                    )
                )
            self.client.upload_records(
                collection_name=collection_name,
                records=batch_records,
            )
        return True

    def search_by_vector(
        self,
        collection_name: str,
        vector: List[float],
        metadatas: Optional[List[dict]] = None,
        limit: Optional[int] = 10,
    ):
        if not self.is_collection_exists(collection_name):
            self.logger.error(f"Collection {collection_name} does not exist")
            return False
        return self.client.search(
            collection_name=collection_name,
            query_vector=vector,
            limit=limit,
            query_filter=metadatas,
        )
