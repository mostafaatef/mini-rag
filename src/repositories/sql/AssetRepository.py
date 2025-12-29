from .BaseRepository import BaseRepository
from src.helpers.config import Settings
from src.models.schemes.mini_rag_db.sql.schemes.asset import Asset
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, List


class AssetRepository(BaseRepository):
    def __init__(self, db_client: AsyncSession, app_settings: Settings):
        super().__init__(db_client, app_settings)

    @classmethod
    async def init_indexes(cls, db_client: object):
        pass

    async def create_indexes(self):
        pass

    async def create_asset(self, asset: Asset):
        self.session.add(asset)
        await self.session.flush()
        await self.session.refresh(asset)
        return asset

    async def get_asset_by_id(self, asset_id: int):
        # We assume asset_id is the integer primary key
        # If the app passes a UUID string, this logic would need to be :
        # stmt = select(Asset).where(Asset.uuid == asset_id)
        # But for now we stick to ID as PK
        result = await self.session.execute(
            select(Asset).where(Asset.id == int(asset_id))
        )
        return result.scalars().first()

    async def get_assets_by_project_id(
        self, asset_project_id: int, asset_type: str = None
    ) -> List[Asset]:
        query = select(Asset).where(Asset.asset_project_id == int(asset_project_id))

        if asset_type:
            query = query.where(Asset.asset_type == asset_type)

        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def get_asset_by_project_id_and_name(
        self, asset_project_id: int, asset_name: str
    ):
        query = select(Asset).where(
            Asset.asset_project_id == int(asset_project_id),
            Asset.asset_name == asset_name,
        )
        result = await self.session.execute(query)
        return result.scalars().first()

    async def delete_asset_by_project_id_and_id(
        self, asset_project_id: int, asset_id: int
    ):
        query = delete(Asset).where(
            Asset.asset_project_id == int(asset_project_id), Asset.id == int(asset_id)
        )
        result = await self.session.execute(query)
        return result.rowcount
