import sys
import os

# Add the project root directory to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from fastapi import FastAPI, Response
from src.routes import base, data, nlp
from motor.motor_asyncio import AsyncIOMotorClient
from src.helpers.config import get_settings
from src.repositories import ProjectRepository, ChunkRepository, AssetRepository
from src.stores.llm.LLMProviderFactory import LLMProviderFactory
from src.stores.vectordbs.VectorDBProviderFactory import VectorDBProviderFactory
from src.stores.llm.templates.template_parser import TemplateParser
from contextlib import asynccontextmanager


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()
    app.mongodb_connection = AsyncIOMotorClient(settings.MONGODB_URL)
    app.mongodb_db_client = app.mongodb_connection[settings.MONGODB_DB]
    app.app_settings = settings

    # Initialize DB Indexes
    await ProjectRepository.init_indexes(app.mongodb_db_client)
    await AssetRepository.init_indexes(app.mongodb_db_client)
    await ChunkRepository.init_indexes(app.mongodb_db_client)

    # Initialize LLM Provider
    llm_provider_factory = LLMProviderFactory(settings)
    app.generation_llm_provider = llm_provider_factory.create_provider(
        settings.GENERATION_BACKEND_LLM
    )
    app.embedding_llm_provider = llm_provider_factory.create_provider(
        settings.EMBEDDING_BACKEND_LLM
    )
    app.generation_llm_provider.set_generation_model(settings.GENERATION_MODEL_ID)
    app.embedding_llm_provider.set_embedding_model(
        settings.EMBEDDING_MODEL_ID, settings.EMBEDDING_MODEL_SIZE
    )

    # Initialize VectorDB Provider
    vector_db_provider_factory = VectorDBProviderFactory(settings)
    app.vector_db_provider = vector_db_provider_factory.create_provider(
        settings.VECTOR_DB_BACKEND
    )
    app.vector_db_provider.connect()

    app.template_parser = TemplateParser(language=settings.DEFAULT_LANG)

    yield

    app.mongodb_connection.close()
    app.vector_db_provider.disconnect()


app = FastAPI(lifespan=lifespan)


@app.get("/api/v1/health")
async def health_check():
    return {"status": "ok"}


@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    return Response(status_code=204)


app.include_router(base.base_router)
app.include_router(data.data_router)
app.include_router(nlp.nlp_router)
