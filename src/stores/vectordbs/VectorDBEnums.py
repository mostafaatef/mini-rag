from enum import Enum


class VectorDBEnum(Enum):
    QDRANT = "QDRANT"
    PGVECTOR = "PGVECTOR"


class QdrantDistanceMethodEnums(Enum):
    COSINE = "cosine"
    DOT = "dot"


class PgVectorDistanceMethodEnums(Enum):
    COSINE = "vector_cosine_ops"
    L2 = "vector_l2_ops"
    DOT = "vector_dot_ops"


class PgVectorTablesSchemeEnums(Enum):
    ID = "id"
    TEXT = "text"
    VECTOR = "vector"
    METADATA = "metadata"
    CHUNK_ID = "chunk_id"
    _PREFIX = "pgVector"


class PgVectorIndexTypeEnums(Enum):
    HNSW = "hnsw"
    IVFFLAT = "ivfflat"
