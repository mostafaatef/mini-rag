
from fastapi import FastAPI, Response 
from routes import base, data
from motor.motor_asyncio import AsyncIOMotorClient
from helpers.config import get_settings
from repositories import ProjectRepository, ChunkRepository, AssetRepository

app = FastAPI()

@app.on_event("startup")
async def startup():
    settings = get_settings()
    app.mongodb_connection = AsyncIOMotorClient(settings.MONGODB_URL)
    app.mongodb_db_client = app.mongodb_connection[settings.MONGODB_DB]

    # Initialize DB Indexes
    await ProjectRepository.init_indexes(app.mongodb_db_client)
    await AssetRepository.init_indexes(app.mongodb_db_client)
    await ChunkRepository.init_indexes(app.mongodb_db_client)

@app.on_event("shutdown")
async def shutdown():
    app.mongodb_connection.close()

app.include_router(base.base_router)
app.include_router(data.data_router)

@app.get("/api/v1/health")
async def health_check():
    return {"status": "ok"}

@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    return Response(status_code=204)



