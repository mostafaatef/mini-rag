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
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from src.utils.metrics import setup_metrics


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()
    app.app_settings = settings

    if settings.DATABASE_TYPE == "SQL":
        app.postgres_connection = create_async_engine(
            f"postgresql+asyncpg://{settings.POSTGRES_USERNAME}:{settings.POSTGRES_PASSWORD}@{settings.POSTGRES_HOST}:{settings.POSTGRES_PORT}/{settings.POSTGRES_MAIN_DATABASE}"
        )
        app.db_engine = create_async_engine(app.postgres_connection.url)
        app.db_client = sessionmaker(
            app.db_engine, class_=AsyncSession, expire_on_commit=False
        )
        # Initialize DB Indexes (No-op for SQL usually handled by migrations)
        await ProjectRepository.init_indexes(None)
        await AssetRepository.init_indexes(None)
        await ChunkRepository.init_indexes(None)
    else:
        app.mongodb_connection = AsyncIOMotorClient(settings.MONGODB_URL)
        app.mongodb_db_client = app.mongodb_connection[settings.MONGODB_DB]
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

    db_client_for_vdb = None
    app.vector_db_engine = None

    if settings.VECTOR_DB_BACKEND == "PGVECTOR":
        vdb_url = getattr(settings, "VECTOR_POSTGRES_DB_URL", None)
        if vdb_url:
            # Ensure it uses asyncpg driver
            if "postgresql+asyncpg://" not in vdb_url:
                vdb_url = vdb_url.replace("postgresql://", "postgresql+asyncpg://")
            app.vector_db_engine = create_async_engine(vdb_url)
            db_client_for_vdb = app.vector_db_engine
        else:
            db_client_for_vdb = getattr(app, "db_engine", None)
    elif settings.DATABASE_TYPE == "SQL":
        db_client_for_vdb = getattr(app, "db_engine", None)
    else:
        db_client_for_vdb = getattr(app, "mongodb_db_client", None)

    app.vector_db_provider = vector_db_provider_factory.create_provider(
        settings.VECTOR_DB_BACKEND, db_client=db_client_for_vdb
    )
    await app.vector_db_provider.connect()

    app.template_parser = TemplateParser(language=settings.DEFAULT_LANG)

    yield

    if settings.DATABASE_TYPE == "SQL":
        await app.db_engine.dispose()
    else:
        app.mongodb_connection.close()

    if getattr(app, "vector_db_engine", None):
        await app.vector_db_engine.dispose()

    await app.vector_db_provider.disconnect()


app = FastAPI(lifespan=lifespan)
setup_metrics(app)


@app.get("/api/v1/health")
async def health_check():
    return {"status": "ok"}


@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    return Response(status_code=204)


app.include_router(base.base_router)
app.include_router(data.data_router)
app.include_router(nlp.nlp_router)
