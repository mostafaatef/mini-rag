from src.helpers.config import get_settings
from fastapi import Request


async def get_db_client(request: Request):
    app_settings = get_settings()

    if app_settings.DATABASE_TYPE == "SQL":
        async with request.app.db_client() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise
    else:
        yield request.app.mongodb_db_client
