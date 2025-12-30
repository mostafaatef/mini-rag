import asyncio
from qdrant_client import AsyncQdrantClient, models
import os


async def check():
    db_path = "/tmp/qdrant_test"
    if not os.path.exists(db_path):
        os.makedirs(db_path)
    client = AsyncQdrantClient(path=db_path)
    print(
        f"upload_records is coroutine: {asyncio.iscoroutinefunction(client.upload_records)}"
    )
    print(
        f"upload_points is coroutine: {asyncio.iscoroutinefunction(client.upload_points)}"
    )
    print(f"upsert is coroutine: {asyncio.iscoroutinefunction(client.upsert)}")

    # Try calling it
    try:
        res = client.upload_records("test", [])
        print(f"Result of call: {res}")
    except Exception as e:
        print(f"Error calling: {e}")

    await client.close()


if __name__ == "__main__":
    asyncio.run(check())
