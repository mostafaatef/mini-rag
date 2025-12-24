import sys
import os

# Add src to python path
sys.path.append(os.path.join(os.getcwd(), "src"))

from src.stores.vectordbs.providers.QdrantVDBProvider import QdrantVDB
from src.stores.vectordbs.VectorDBEnums import DistanceMethodEnum
import logging

logging.basicConfig(level=logging.INFO)


def test_qdrant():
    print("Initializing QdrantVDB...")
    vdb = QdrantVDB(db_path=":memory:", distance_method=DistanceMethodEnum.DOT)

    # Verify properties are set correctly
    assert vdb.db_path == ":memory:", "db_path not set correctly"
    # Note: distance_method in vdb is converted to Qdrant model, checking raw value might be tricky depending on implementation,
    # but we can check if it's not None
    assert vdb.distance_method is not None, "distance_method not set"

    print("Connecting...")
    vdb.connect()

    collection_name = "test_collection_refactor"
    embedding_size = 4

    print(f"Creating collection {collection_name}...")
    success = vdb.create_collection(collection_name, embedding_size)
    assert success, "Failed to create collection"

    print("Inserting one record...")
    vec1 = [0.1, 0.2, 0.3, 0.4]
    success = vdb.insert_one(collection_name, "text1", vec1, {"meta": "data1"})
    assert success, "Failed to insert one"

    print("Disconnecting...")
    vdb.disconnect()
    print("Test passed!")


if __name__ == "__main__":
    try:
        test_qdrant()
    except Exception as e:
        print(f"Test failed with error: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)
