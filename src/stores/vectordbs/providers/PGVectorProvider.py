import psycopg2
from psycopg2.extras import execute_values
from pgvector.psycopg2 import register_vector
import uuid
from typing import List, Optional
from logging import getLogger
from ..VectorDBInterface import VectorDBInterface
from .BaseVDBProvider import BaseVectorDBProvider
from ..VectorDBEnums import DistanceMethodEnum


class PGVectorProvider(BaseVectorDBProvider):
    def __init__(self, db_url: str, distance_method: DistanceMethodEnum):
        # We don't use db_path for PG, but BaseVectorDBProvider expects it.
        # We can pass None or empty string as it's not used.
        super().__init__(db_path="", distance_method=distance_method)
        self.db_url = db_url
        self.conn = None
        self.logger = getLogger(__name__)

        # Map distance enum to PGVector operators
        # <-> : Euclidean distance (L2)
        # <=> : Cosine distance
        # <#> : Inner product (Negative dot product)
        self.distance_operator = "<=>"  # Default Cosine
        if distance_method == DistanceMethodEnum.L2:
            self.distance_operator = "<->"
        elif distance_method == DistanceMethodEnum.IP:
            self.distance_operator = "<#>"  # Note: For inner product, we usually want max, but PG operators sort ASC.
            # <#> is negative inner product, so sorting ASC gives max inner product.
        elif distance_method == DistanceMethodEnum.DOT:
            self.distance_operator = "<#>"

        self.logger.info("PGVectorProvider initialized")

    def connect(self):
        try:
            self.conn = psycopg2.connect(self.db_url)
            # Enable auto-commit for simpler handling, or manage transactions explicitly
            self.conn.autocommit = True

            # Register the vector type
            register_vector(self.conn)

            self.logger.info("Connected to PGVector")

            # Ensure extension exists
            with self.conn.cursor() as cur:
                cur.execute("CREATE EXTENSION IF NOT EXISTS vector;")

        except Exception as e:
            self.logger.error(f"Failed to connect to PGVector: {e}")
            raise e

    def disconnect(self):
        if self.conn:
            self.conn.close()

    def _sanitize_table_name(self, name: str) -> str:
        # Simple sanitization to prevent SQL injection via table names
        # Assuming collection names are alphanumeric + underscore
        return "".join(c for c in name if c.isalnum() or c == "_")

    def is_collection_exists(self, collection_name: str) -> bool:
        table_name = self._sanitize_table_name(collection_name)
        with self.conn.cursor() as cur:
            cur.execute(
                "SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = %s);",
                (table_name,),
            )
            return cur.fetchone()[0]

    def list_all_collections(self) -> list:
        # This is tricky as we might have other tables.
        # We can query tables having a 'embedding' column of type vector.
        with self.conn.cursor() as cur:
            cur.execute("""
                SELECT table_name 
                FROM information_schema.columns 
                WHERE udt_name = 'vector' 
                GROUP BY table_name;
            """)
            return [row[0] for row in cur.fetchall()]

    def create_collection(
        self, collection_name: str, embedding_size: int, do_reset: bool = False
    ) -> bool:
        table_name = self._sanitize_table_name(collection_name)

        if self.is_collection_exists(table_name):
            if do_reset:
                self.delete_collection(table_name)
            else:
                self.logger.error(f"Collection {table_name} already exists")
                return False

        # Create table
        # We store id, text, metadata (jsonb), embedding (vector)
        query = f"""
        CREATE TABLE {table_name} (
            id UUID PRIMARY KEY,
            text TEXT,
            metadata JSONB,
            embedding vector({embedding_size})
        );
        """
        try:
            with self.conn.cursor() as cur:
                cur.execute(query)
                # Create an index for faster search (ivfflat is common)
                # Note: Index creation usually requires some data first for optimal lists,
                # but we can create HNSW index for better performance/recall tradeoff if pgvector version supports it (>=0.5.0)
                # Let's try creating HNSW index by default as it's state of the art.
                try:
                    cur.execute(
                        f"CREATE INDEX ON {table_name} USING hnsw (embedding vector_cosine_ops);"
                    )
                except Exception as index_err:
                    self.logger.warning(
                        f"Could not create HNSW index (maybe pgvector version is old?), falling back or ignoring: {index_err}"
                    )

            return True
        except Exception as e:
            self.logger.error(f"Error creating collection: {e}")
            return False

    def delete_collection(self, collection_name: str):
        table_name = self._sanitize_table_name(collection_name)
        if self.is_collection_exists(table_name):
            with self.conn.cursor() as cur:
                cur.execute(f"DROP TABLE IF EXISTS {table_name};")

    def get_collection_info(self, collection_name: str) -> dict:
        # Minimal info
        table_name = self._sanitize_table_name(collection_name)
        if not self.is_collection_exists(table_name):
            return {}

        with self.conn.cursor() as cur:
            cur.execute(f"SELECT count(*) FROM {table_name};")
            count = cur.fetchone()[0]
            return {"name": table_name, "count": count}

    def insert_one(
        self,
        collection_name: str,
        text: str,
        vector: List[float],
        metadatas: Optional[dict] = None,
        record_id: Optional[str] = None,
    ):
        return self.insert_many(
            collection_name,
            [text],
            [metadatas] if metadatas else None,
            [vector],
            [record_id] if record_id else None,
        )

    def insert_many(
        self,
        collection_name: str,
        texts: List[str],
        metadatas: Optional[List[dict]] = None,
        vectors: Optional[List[List[float]]] = None,
        record_ids: Optional[List[str]] = None,
        batch_size: Optional[int] = 100,
    ):
        table_name = self._sanitize_table_name(collection_name)
        if not self.is_collection_exists(table_name):
            self.logger.error(f"Collection {table_name} does not exist")
            return False

        if metadatas is None:
            metadatas = [None] * len(texts)
        if vectors is None:
            # This should ideally not happen in this flow as we expect vectors
            return False
        if record_ids is None:
            record_ids = [str(uuid.uuid4()) for _ in range(len(texts))]

        data = []
        for i in range(len(texts)):
            # Ensure metadata is json compatible dict or None
            meta = metadatas[i] if metadatas[i] else {}
            data.append(
                (record_ids[i], texts[i], psycopg2.extras.Json(meta), vectors[i])
            )

        try:
            with self.conn.cursor() as cur:
                execute_values(
                    cur,
                    f"INSERT INTO {table_name} (id, text, metadata, embedding) VALUES %s",
                    data,
                )
            return True
        except Exception as e:
            self.logger.error(f"Error inserting records: {e}")
            return False

    def search_by_vector(
        self,
        collection_name: str,
        vector: List[float],
        metadatas: Optional[List[dict]] = None,
        limit: Optional[int] = 10,
    ):
        table_name = self._sanitize_table_name(collection_name)
        if not self.is_collection_exists(table_name):
            self.logger.error(f"Collection {table_name} does not exist")
            return False

        # Build Metadata Filter (simple equality for now, or use JSONB containment @>)
        # current interface assumes metadatas is a filter dict?
        # Interface says 'metadatas: Optional[List[dict]] = None' is query_filter in Qdrant.
        # Let's assume it's a dict for exact match on fields.

        where_clause = ""
        params = [vector, limit]

        # NOTE: Handling metadata filter in raw SQL is complex.
        # For this PoC, we might skip complex filtering or implement basic JSON containment.
        # Qdrant implementation passed `metadatas` as `query_filter`.

        query = f"""
        SELECT text, metadata, embedding <=> %s as score, id
        FROM {table_name}
        ORDER BY score ASC
        LIMIT %s;
        """

        # Note on score: PGVector returns distance. Smaller is better for distance.
        # But retrieval systems usually expect Similarity (Higher is better).
        # Cosine Distance = 1 - Cosine Similarity.
        # So Similarity = 1 - Distance.

        results = []
        try:
            with self.conn.cursor() as cur:
                cur.execute(query, (vector, limit))
                rows = cur.fetchall()
                for row in rows:
                    text, metadata, distance, id = row
                    score = 1 - distance  # Convert to similarity if using cosine

                    # Construct a Qdrant-like object or just a plain dict as expected by Controller
                    # The Controller expects objects with .dict() method or accessing fields?
                    # Controller: `return [item.dict() for item in result]` (Qdrant returns ScoredPoint)
                    # We need to return an object that mimics ScoredPoint structure

                    # Wait, Controller code:
                    # `result = self.vector_client.search_by_vector(...)`
                    # `return [item.dict() for item in result]`

                    # So we should return a list of objects having a .dict() method.
                    results.append(
                        ScoredRecord(id=id, score=score, text=text, metadata=metadata)
                    )

            return results
        except Exception as e:
            self.logger.error(f"Error searching: {e}")
            return []


class ScoredRecord:
    def __init__(self, id, score, text, metadata):
        self.id = str(id)
        self.score = score
        self.payload = {"text": text, "metadata": metadata}
        self.version = 0  # Dummy

    def dict(self):
        return {
            "id": self.id,
            "score": self.score,
            "payload": self.payload,
            "version": self.version,
        }
