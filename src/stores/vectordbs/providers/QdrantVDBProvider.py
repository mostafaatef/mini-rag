from qdrant_client import AsyncQdrantClient, models
import uuid
from ..VectorDBInterface import VectorDBInterface
from logging import getLogger
from typing import List, Optional

from .BaseVDBProvider import BaseVectorDBProvider
from ..VectorDBEnums import VectorDBEnum, QdrantDistanceMethodEnums
from src.models.schemes.mini_rag_db.nosql import RetrievedChunkIndex


class QdrantVDBProvider(BaseVectorDBProvider):
    def __init__(self, db_path: str, distance_method: str):
        super().__init__(db_path, distance_method)
        self.distance_method = models.Distance.COSINE

        if distance_method == QdrantDistanceMethodEnums.DOT.value:
            self.distance_method = models.Distance.DOT
        elif distance_method == QdrantDistanceMethodEnums.COSINE.value:
            self.distance_method = models.Distance.COSINE

        self.logger.info("QdrantVDB initialized")

    async def connect(self):
        import asyncio

        retries = 3
        for i in range(retries):
            try:
                self.client = AsyncQdrantClient(path=self.db_path)
                self.logger.info("QdrantVDB connected")
                return True
            except Exception as e:
                if i < retries - 1:
                    self.logger.warning(
                        f"Connection failed (attempt {i + 1}/{retries}), retrying in 1s: {e}"
                    )
                    await asyncio.sleep(1)
                else:
                    self.logger.error(
                        f"Failed to connect to QdrantVDB after {retries} attempts"
                    )
                    raise e

    async def disconnect(self):
        if self.client:
            await self.client.close()

    async def is_collection_exists(self, collection_name: str) -> bool:
        return await self.client.collection_exists(collection_name)

    async def list_all_collections(self) -> list:
        collections = await self.client.get_collections()
        return collections.collections

    async def get_collection_info(self, collection_name: str) -> dict:
        info = await self.client.get_collection(collection_name)
        return info.dict()

    async def delete_collection(self, collection_name: str):
        if await self.is_collection_exists(collection_name):
            await self.client.delete_collection(collection_name)

    async def create_collection(
        self, collection_name: str, embedding_size: int, do_reset: bool = False
    ):
        if await self.is_collection_exists(collection_name):
            if do_reset:
                await self.delete_collection(collection_name)
            else:
                self.logger.error(f"Collection {collection_name} already exists")
                return False
        await self.client.create_collection(
            collection_name=collection_name,
            vectors_config=models.VectorParams(
                size=embedding_size,
                distance=self.distance_method,
            ),
        )
        return True

    async def insert_one(
        self,
        collection_name: str,
        text: str,
        vector: List[float],
        metadatas: Optional[dict] = None,
        record_id: Optional[str] = None,
    ):
        if not await self.is_collection_exists(collection_name):
            self.logger.error(f"Collection {collection_name} does not exist")
            return False

        record_id = record_id if record_id else str(uuid.uuid4())

        await self.client.upload_points(
            collection_name=collection_name,
            points=[
                models.PointStruct(
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

    async def insert_many(
        self,
        collection_name: str,
        texts: List[str],
        metadatas: Optional[List[dict]] = None,
        vectors: Optional[List[List[float]]] = None,
        record_ids: Optional[List[str]] = None,
        batch_size: Optional[int] = 100,
    ):
        if not await self.is_collection_exists(collection_name):
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
                    models.PointStruct(
                        id=batch_record_ids[j],
                        vector=batch_vectors[j],
                        payload={
                            "text": batch_texts[j],
                            "metadata": batch_metadatas[j],
                        },
                    )
                )
            await self.client.upload_points(
                collection_name=collection_name,
                points=batch_records,
            )
        return True

    async def search_by_vector(
        self,
        collection_name: str,
        vector: List[float],
        metadatas: Optional[List[dict]] = None,
        limit: Optional[int] = 10,
    ) -> List[RetrievedChunkIndex]:
        if not await self.is_collection_exists(collection_name):
            self.logger.error(f"Collection {collection_name} does not exist")
            return None

        results = await self.client.search(
            collection_name=collection_name,
            query_vector=vector,
            limit=limit,
            query_filter=metadatas,
        )

        if not results:
            return None

        retrieved_chunk_indices = []
        for result in results:
            retrieved_chunk_index = RetrievedChunkIndex(
                id=str(result.id),
                text=result.payload["text"],
                score=result.score,
                metadata=result.payload.get("metadata"),
                payload=result.payload,
            )
            retrieved_chunk_indices.append(retrieved_chunk_index)
        return retrieved_chunk_indices
