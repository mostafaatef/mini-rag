import asyncio
from unittest.mock import MagicMock
import sys
import os

# Add src to path
sys.path.append(os.path.join(os.getcwd(), 'src'))

# Mocking settings and database
class MockSettings:
    pass

async def test_invalid_id_handling():
    try:
        from repositories.AssetRepository import AssetRepository
        from bson.errors import InvalidId
        
        # Mock DB client
        mock_db_client = MagicMock()
        mock_collection = MagicMock()
        mock_db_client.__getitem__ = MagicMock(return_value=mock_collection)
        
        repo = AssetRepository(mock_db_client, MockSettings())
        repo.collection = mock_collection
        
        print("Testing get_asset_by_id with invalid ID 'string'...")
        
        # We need to test the actual method execution, but since we are mocking collection, 
        # the find_one call assumes the input to it is valid or handled before.
        # Wait, the InvalidId happens at ObjectId("string") instantiation, which is BEFORE find_one is awaited.
        # So mocking find_one return value doesn't matter for the exception.
        
        # However, since find_one is async, we need a mock that can be awaited if the code reaches it.
        # But for invalid ID, it should NOT reach await find_one if ObjectId throws.
        # Wait, the code is:
        # await self.collection.find_one({"_id": ObjectId(asset_id)})
        # ObjectId(asset_id) is evaluated eagerly before awaiting.
        
        # SO, if we call repo.get_asset_by_id("string"), it enters the method.
        # It tries ObjectId("string"). BAM! InvalidId.
        # Our try/except should catch it and return None.
        
        result = await repo.get_asset_by_id("string")
        
        if result is None:
            print("SUCCESS: Result is None for invalid ID.")
        else:
            print(f"FAILURE: Result is {result}, expected None.")
            
    except ImportError as e:
        print(f"Import Error: {e}")
    except Exception as e:
        print(f"FAILURE: Unexpected exception raised: {e}")

if __name__ == "__main__":
    asyncio.run(test_invalid_id_handling())
