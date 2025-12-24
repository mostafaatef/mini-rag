from enum import Enum


class VectorDBEnum(Enum):
    QDRANT = "QDRANT"


class DistanceMethodEnum(Enum):
    L2 = "L2"
    IP = "IP"
    COSINE = "COSINE"
    DOT = "DOT"
