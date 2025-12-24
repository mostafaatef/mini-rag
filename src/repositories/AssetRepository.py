from .BaseRepository import BaseRepository
from src.models.schemes.db_schemes.asset import Asset
from src.helpers.config import Settings
from src.models.enums.DatabaseEnum import DatabaseEnum
from bson import ObjectId
from bson.errors import InvalidId

class AssetRepository(BaseRepository):
    def __init__(self, db_client: object, app_settings: Settings):
        super().__init__(db_client, app_settings)
        self.collection = self.db_client[DatabaseEnum.COLLECTION_ASSETS_NAME]

    async def create_indexes(self):
        indexes = Asset.get_indexes()
        for index in indexes:
            await self.collection.create_index(
                index["key"],
                name=index["name"],
                unique=index["unique"]
            )

    @classmethod
    async def init_indexes(cls, db_client: object):
        collection = db_client[DatabaseEnum.COLLECTION_ASSETS_NAME]
        indexes = Asset.get_indexes()
        for index in indexes:
            await collection.create_index(
                index["key"],
                name=index["name"],
                unique=index["unique"]
            )
    
    async def create_indexes(self):
        indexes = Asset.get_indexes()
        for index in indexes:
            await self.collection.create_index(
                index["key"],
                name=index["name"],
                unique=index["unique"]
            )
    
    async def create_asset(self, asset: Asset):
        result = await self.collection.insert_one(asset.dict(by_alias=True, exclude_none=True))
        asset.id = result.inserted_id
        return asset

    async def get_asset_by_id(self, asset_id: str):
        try:
            record = await self.collection.find_one({"_id": ObjectId(asset_id)})
        except InvalidId:
            return None
        if record is None:
            return None
        return Asset(**record)

    async def get_assets_by_project_id(self, asset_project_id: str, asset_type: str = None):
        query = {"asset_project_id": ObjectId(asset_project_id)}
        if asset_type:
            query["asset_type"] = asset_type
        cursor = self.collection.find(query)
        assets = []
        async for asset_doc in cursor:
            assets.append(Asset(**asset_doc))
        return assets

    async def get_asset_by_project_id_and_name(self, asset_project_id: str, asset_name: str):
        try:
            record = await self.collection.find_one({"asset_project_id": ObjectId(asset_project_id),"asset_name": asset_name})
        except InvalidId:
            return None
        if record is None:
            return None
        return Asset(**record)
    
    async def delete_asset_by_project_id_and_id(self, asset_project_id: str, asset_id: str):
        result = await self.collection.delete_one({"asset_project_id": ObjectId(asset_project_id),"_id": ObjectId(asset_id)})
        return result.deleted_count
