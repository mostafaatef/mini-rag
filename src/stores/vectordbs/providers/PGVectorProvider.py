from typing import List, Optional
from logging import getLogger
from .BaseVDBProvider import BaseVectorDBProvider
from ..VectorDBEnums import (
    PgVectorDistanceMethodEnums,
    PgVectorTablesSchemeEnums,
    PgVectorIndexTypeEnums,
)
from sqlalchemy.sql import text as sql_text
from sqlalchemy.ext.asyncio import AsyncEngine
from src.models.schemes.mini_rag_db.sql import RetrievedChunkIndex
import json


class PGVectorProvider(BaseVectorDBProvider):
    def __init__(
        self,
        db_client: AsyncEngine,
        default_vector_size: int = 768,
        distance_method: str = None,
        index_threshold: int = 1000,
    ):
        # We don't use db_path for PG, but BaseVectorDBProvider expects it.
        super().__init__(
            db_path="",
            distance_method=distance_method,
            default_vector_size=default_vector_size,
            index_threshold=index_threshold,
        )
        self.db_client = db_client
        self.default_vector_size = default_vector_size
        self.pgvector_tables_prefix = PgVectorTablesSchemeEnums._PREFIX.value
        self.default_index_name = (
            lambda collection_name: f"idx_{collection_name}_vector"
        )
        self.logger = getLogger("uvicorn")
        self._collection_exists_cache = set()
        self.index_threshold = index_threshold

        # Map distance enum to PGVector operators
        self.distance_operator = "<=>"  # Default Cosine
        if distance_method == PgVectorDistanceMethodEnums.L2.value:
            self.distance_operator = "<->"
        elif distance_method == PgVectorDistanceMethodEnums.DOT.value:
            self.distance_operator = "<#>"

        self.logger.info("PGVectorProvider initialized")

    async def connect(self):
        try:
            async with self.db_client.connect() as conn:
                await conn.execute(sql_text("CREATE EXTENSION IF NOT EXISTS vector;"))
                await conn.commit()
            self.logger.info("Connected to PGVector & Extension verified")
            return True
        except Exception as e:
            self.logger.error(f"Failed to connect to PGVector: {e}")
            return False

    async def disconnect(self):
        # SQLAlchemy engine disposal is handled in main.lifespan
        pass

    def _sanitize_table_name(self, name: str) -> str:
        return "".join(c for c in name if c.isalnum() or c == "_").lower()

    async def is_collection_exists(self, collection_name: str) -> bool:
        table_name = self._sanitize_table_name(collection_name)
        if table_name in self._collection_exists_cache:
            return True

        query = sql_text(
            "SELECT EXISTS (SELECT FROM pg_tables WHERE tablename = :table_name);"
        )
        async with self.db_client.connect() as conn:
            result = await conn.execute(query, {"table_name": table_name})
            exists = bool(result.scalar())
            if exists:
                self._collection_exists_cache.add(table_name)
            return exists

    async def list_all_collections(self) -> list:
        # We query tables having an 'embedding' column of type vector.
        query = sql_text("""
            SELECT table_name 
            FROM information_schema.columns 
            WHERE udt_name = 'vector' 
            GROUP BY table_name;
        """)
        async with self.db_client.connect() as conn:
            result = await conn.execute(query)
            return [row[0] for row in result.fetchall()]

    async def create_collection(
        self, collection_name: str, embedding_size: int, do_reset: bool = False
    ) -> bool:
        table_name = self._sanitize_table_name(collection_name)

        if await self.is_collection_exists(table_name):
            if do_reset:
                await self.delete_collection(table_name)
            else:
                self.logger.info(f"Collection {table_name} already exists")
                return False

        self.logger.info(f"Creating collection {table_name}")

        query = sql_text(f"""
        CREATE TABLE {table_name} (
            {PgVectorTablesSchemeEnums.ID.value} bigserial PRIMARY KEY,
            {PgVectorTablesSchemeEnums.CHUNK_ID.value} INTEGER,
            {PgVectorTablesSchemeEnums.TEXT.value} TEXT,
            {PgVectorTablesSchemeEnums.METADATA.value} JSONB DEFAULT '{{}}',
            {PgVectorTablesSchemeEnums.VECTOR.value} vector({embedding_size}),
            FOREIGN KEY ({PgVectorTablesSchemeEnums.CHUNK_ID.value}) REFERENCES chunks(id) ON DELETE CASCADE
        );
        """)

        try:
            async with self.db_client.connect() as conn:
                await conn.execute(query)
                await conn.commit()

            self._collection_exists_cache.add(table_name)

            # Defer index creation until explicitly requested or after significant data load
            # for initial performance.
            # We can create it here if embedding size is small enough, but let's keep it optional
            # or add a separate method for it.
            # await self.create_index(collection_name)

            return True
        except Exception as e:
            self.logger.error(f"Error creating collection: {e}")
            return False

    async def is_index_exists(self, table_name: str, index_name: str) -> bool:
        query = sql_text(
            "SELECT indexname FROM pg_indexes WHERE tablename = :table_name AND indexname = :index_name;"
        )
        async with self.db_client.connect() as conn:
            result = await conn.execute(
                query, {"table_name": table_name, "index_name": index_name}
            )
            return bool(result.scalar_one_or_none())

    async def create_index(
        self, collection_name: str, index_type: str = PgVectorIndexTypeEnums.HNSW.value
    ):
        table_name = self._sanitize_table_name(collection_name)
        index_name = self.default_index_name(table_name)

        if await self.is_index_exists(table_name, index_name):
            return False

        async with self.db_client.connect() as conn:
            count = await conn.execute(sql_text(f"SELECT COUNT(*) FROM {table_name};"))
            count = count.scalar_one()
            if count < self.index_threshold:
                return False
        self.logger.info(
            f"Creating index for {table_name} with threshold {self.index_threshold}"
        )

        # Map driver operator to index ops
        index_ops = "vector_cosine_ops"
        if self.distance_operator == "<->":
            index_ops = "vector_l2_ops"
        elif self.distance_operator == "<#>":
            index_ops = "vector_ip_ops"

        index_query = sql_text(
            f"CREATE INDEX IF NOT EXISTS {index_name} ON {table_name} USING {index_type} ({PgVectorTablesSchemeEnums.VECTOR.value} {index_ops});"
        )

        async with self.db_client.connect() as conn:
            try:
                await conn.execute(index_query)
                await conn.commit()
                self.logger.info(f"{index_type} index created for {table_name}")
            except Exception as index_err:
                self.logger.warning(f"Could not create {index_type} index: {index_err}")

    async def reset_index(
        self,
        collection_name: str,
        index_type: str = PgVectorIndexTypeEnums.HNSW.value,
    ):
        table_name = self._sanitize_table_name(collection_name)
        index_name = self.default_index_name(table_name)
        async with self.db_client.connect() as conn:
            try:
                await conn.execute(sql_text(f"DROP INDEX IF EXISTS {index_name};"))
                await conn.commit()
                self.logger.info(f"Index {index_name} dropped for {table_name}")
            except Exception as index_err:
                self.logger.warning(f"Could not drop index {index_name}: {index_err}")
        return await self.create_index(collection_name, index_type)

    async def delete_collection(self, collection_name: str):
        table_name = self._sanitize_table_name(collection_name)
        query = sql_text(f"DROP TABLE IF EXISTS {table_name};")
        async with self.db_client.connect() as conn:
            await conn.execute(query)
            await conn.commit()

        if table_name in self._collection_exists_cache:
            self._collection_exists_cache.remove(table_name)

        self.logger.info(f"Collection {table_name} deleted")

    async def get_collection_info(self, collection_name: str) -> dict:
        table_name = self._sanitize_table_name(collection_name)
        if not await self.is_collection_exists(table_name):
            return {}

        query_info = sql_text(
            "SELECT schemaname, tablename, tableowner FROM pg_tables WHERE tablename = :table_name;"
        )
        query_count = sql_text(f"SELECT COUNT(*) FROM {table_name};")

        async with self.db_client.connect() as conn:
            info_result = await conn.execute(query_info, {"table_name": table_name})
            count_result = await conn.execute(query_count)

            info_row = info_result.fetchone()
            if not info_row:
                return {}

            return {
                "name": table_name,
                "count": count_result.scalar(),
                "info": dict(info_row._mapping),
            }

    async def insert_one(
        self,
        collection_name: str,
        text: str,
        vector: List[float],
        metadatas: Optional[dict] = None,
        record_id: Optional[str] = None,
    ):
        return await self.insert_many(
            collection_name,
            [text],
            [metadatas] if metadatas else None,
            [vector],
            [record_id] if record_id else None,
        )

    async def insert_many(
        self,
        collection_name: str,
        texts: List[str],
        metadatas: Optional[List[dict]] = None,
        vectors: Optional[List[List[float]]] = None,
        record_ids: Optional[List[str]] = None,
        batch_size: Optional[int] = 100,
    ):
        table_name = self._sanitize_table_name(collection_name)
        if not await self.is_collection_exists(table_name):
            self.logger.error(f"Collection {table_name} does not exist")
            return False

        if metadatas is None:
            metadatas = [None] * len(texts)
        if vectors is None:
            return False

        columns = [
            PgVectorTablesSchemeEnums.CHUNK_ID.value,
            PgVectorTablesSchemeEnums.TEXT.value,
            PgVectorTablesSchemeEnums.METADATA.value,
            PgVectorTablesSchemeEnums.VECTOR.value,
        ]

        query = sql_text(
            f"INSERT INTO {table_name} ({', '.join(columns)}) VALUES (:chunk_id, :text, :metadata, CAST(:embedding AS vector))"
        )

        try:
            async with self.db_client.connect() as conn:
                for i in range(0, len(texts), batch_size):
                    batch_end = min(i + batch_size, len(texts))
                    params = []
                    for j in range(i, batch_end):
                        meta = metadatas[j] if metadatas[j] else {}
                        # Extract chunk_id from metadata if available (from NLPController.index_into_vdb)
                        chunk_id = meta.get("id") or meta.get("_id")

                        params.append(
                            {
                                "chunk_id": int(chunk_id)
                                if isinstance(chunk_id, (int, str))
                                and str(chunk_id).isdigit()
                                else None,
                                "text": texts[j],
                                "metadata": json.dumps(meta),
                                "embedding": str(vectors[j]),
                            }
                        )
                    await conn.execute(query, params)
                await conn.commit()
            return True
        except Exception as e:
            self.logger.error(f"Error inserting records: {e}")
            return False

    async def search_by_vector(
        self,
        collection_name: str,
        vector: List[float],
        metadatas: Optional[List[dict]] = None,
        limit: Optional[int] = 10,
    ):
        table_name = self._sanitize_table_name(collection_name)
        if not await self.is_collection_exists(table_name):
            self.logger.error(f"Collection {table_name} does not exist")
            return []

        query = sql_text(f"""
            SELECT {PgVectorTablesSchemeEnums.TEXT.value}, 
                   {PgVectorTablesSchemeEnums.METADATA.value}, 
                   {PgVectorTablesSchemeEnums.VECTOR.value} {self.distance_operator} CAST(:vector AS vector) as distance, 
                   {PgVectorTablesSchemeEnums.ID.value}
            FROM {table_name}
            ORDER BY distance ASC
            LIMIT :limit;
        """)

        results = []
        try:
            async with self.db_client.connect() as conn:
                result = await conn.execute(
                    query, {"vector": str(vector), "limit": limit}
                )
                rows = result.fetchall()
                for row in rows:
                    text, metadata, distance, id = row
                    score = (
                        1 - distance if self.distance_operator == "<=>" else distance
                    )

                    results.append(
                        RetrievedChunkIndex(
                            id=str(id),
                            score=score,
                            text=text,
                            metadata=metadata,
                            payload={"text": text, "metadata": metadata},
                        )
                    )

            return results
        except Exception as e:
            self.logger.error(f"Error searching: {e}")
            return []
