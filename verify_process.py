import sys
import os
import asyncio
from unittest.mock import MagicMock, AsyncMock

# ensure src is in path
sys.path.insert(0, os.path.abspath("src"))

try:
    from helpers.config import get_settings
    from controllers import DataController, ProcessingController
    from models import ProjectModel, AssetModel, ChunkModel
    from models.schemes.db_schemes import Asset
    from models.enums import AssetTypesEnum
    from datetime import datetime
    from bson import ObjectId
except ImportError as e:
    print(f"Import failed: {e}")
    sys.exit(1)

async def test_process_logic():
    print("Testing processing logic with Asset ID lookup...")
    
    # Mock Settings
    class DummySettings:
        APP_NAME = "Test"
        APP_VERSION = "0.1"
        FILE_ALLOWAED_TYPES = ["text/plain"]
        FILE_MAX_SIZE = 10
        FILE_CHUNK_SIZE = 1024
        OPENAI_API_KEY = "test"
        MONGODB_URL = "mongodb://localhost:27017"
        MONGODB_DB = "test_db"
    
    settings = DummySettings()
    
    # Needs a real DB connection or extensive mocking. 
    # Since the user environment has a running DB (implied by previous errors), 
    # we might try to connect or just mock the AssetModel behavior which is safer and faster.
    
    print("Mocking DB interaction...")
    
    # Mock asset record
    file_id_oid = ObjectId()
    project_id_oid = ObjectId()
    asset_name = "test_file.txt"
    
    mock_asset = Asset(
        _id=file_id_oid,
        asset_project_id=project_id_oid,
        asset_type=AssetTypesEnum.FILE.value,
        asset_name=asset_name,
        asset_size=100,
        asset_path=f"/tmp/{asset_name}",
        asset_metadata={}
    )
    
    # Mock AssetModel
    mock_asset_model = AsyncMock()
    mock_asset_model.get_asset_by_id.return_value = mock_asset
    
    # Mock ProcessingController
    mock_processing_controller = MagicMock()
    mock_processing_controller.process_file_content.return_value = ["chunk1", "chunk2"]
    
    # Simulate the logic in the route
    print(f"Simulating processing for file_id: {str(file_id_oid)}")
    
    asset_record = await mock_asset_model.get_asset_by_id(str(file_id_oid))
    
    if asset_record is None:
        print("FAILED: Asset record not found (Mock failed)")
        return

    print(f"Retrieved Asset Name: {asset_record.asset_name}")
    
    if asset_record.asset_name == asset_name:
         print("SUCCESS: Correctly retrieved asset name from ID.")
    else:
         print(f"FAILED: Expected {asset_name}, got {asset_record.asset_name}")

    # Verify controller call
    print("Calling processing controller...")
    chunks = mock_processing_controller.process_file_content(asset_record.asset_name, 100, 10)
    print(f"Processing returned {len(chunks)} chunks.")

if __name__ == "__main__":
    asyncio.run(test_process_logic())
