from fastapi import APIRouter, status, Response, Request
from fastapi.responses import JSONResponse
import logging
from src.models.schemes.gen_schemes.NLPRequest import PushRequest, SearchRequest
from src.repositories import ProjectRepository
from src.repositories import ChunkRepository
from src.controllers.NLPController import NLPController
from src.models.enums.ResponseEnum import ResponseMessagesEnum
from src.repositories.db_helper import get_db_client
from src.helpers.config import get_settings, Settings
from fastapi import Depends
from tqdm.auto import tqdm

logger = logging.getLogger(__name__)

nlp_router = APIRouter(
    prefix="/api/v1/nlp",
    tags=["api-v1-nlp"],
)


@nlp_router.post("/index/push/{project_title}")
async def push_index(
    request: Request,
    project_title: str,
    push_request: PushRequest,
    db_client=Depends(get_db_client),
):
    project_repo = ProjectRepository(
        db_client=db_client,
        app_settings=request.app.app_settings,
    )
    project = await project_repo.get_project_or_create_new(project_title)
    if not project:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"message": ResponseMessagesEnum.PROJECT_NOT_FOUND.value},
        )
    chunk_repo = ChunkRepository(
        db_client=db_client,
        app_settings=request.app.app_settings,
    )

    nlp_controller = NLPController(
        vector_client=request.app.vector_db_provider,
        generator_client=request.app.generation_llm_provider,
        embedder_client=request.app.embedding_llm_provider,
        app_settings=request.app.app_settings,
        template_parser=request.app.template_parser,
    )

    # 1. Initialize/Reset collection only once
    await nlp_controller.vector_client.create_collection(
        collection_name=nlp_controller.create_vdb_collection_name(
            project.project_title
        ),
        embedding_size=request.app.embedding_llm_provider.embedding_model_size,
        do_reset=push_request.do_reset,
    )

    has_more = True
    page_no = 1
    page_size = 50
    indexed_chunks = 0

    total_chunks_count = await chunk_repo.get_total_chunks_count(project.id)
    pbar = tqdm(
        total=total_chunks_count, desc="Indexing chunks in vector database", position=0
    )

    while has_more:
        chunks = await chunk_repo.get_chunks_by_project_id(
            project_id=project.id,
            page_no=page_no,
            page_size=page_size,
        )
        if not chunks:
            print(f"DEBUG: No chunks found for page {page_no}. Ending loop.")
            has_more = False
            continue
        print(f"DEBUG: Processing {len(chunks)} chunks for page {page_no}")
        is_indexed = await nlp_controller.index_into_vdb(
            project,
            chunks,
            do_reset=False,  # Crucial: Fixed do_reset loop bug
        )
        print(f"DEBUG: Finished indexing page {page_no}")
        page_no += 1
        if not is_indexed:
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={
                    "signal": ResponseMessagesEnum.PROJECT_INDEX_PUSH_FAILED.value
                },
            )
        indexed_chunks += len(chunks)
        pbar.update(len(chunks))
    # 2. Finalize by creating index (optimized for PGVector)
    await nlp_controller.create_vdb_index(project)
    pbar.close()

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "signal": ResponseMessagesEnum.PROJECT_INDEX_PUSH_SUCCESS.value,
            "inserted_chunks": indexed_chunks,
        },
    )


@nlp_router.get("/index/info/{project_title}")
async def get_index_info(
    request: Request,
    project_title: str,
    db_client=Depends(get_db_client),
):
    project_repo = ProjectRepository(
        db_client=db_client,
        app_settings=request.app.app_settings,
    )
    project = await project_repo.get_project_or_create_new(project_title)
    if not project:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"message": ResponseMessagesEnum.PROJECT_NOT_FOUND.value},
        )
    nlp_controller = NLPController(
        vector_client=request.app.vector_db_provider,
        generator_client=request.app.generation_llm_provider,
        embedder_client=request.app.embedding_llm_provider,
        app_settings=request.app.app_settings,
        template_parser=request.app.template_parser,
    )
    collection_info = await nlp_controller.get_vdb_collection_info(project)
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "message": ResponseMessagesEnum.PROJECT_VDB_INDEX_INFO_SUCCESS.value,
            "collection_info": collection_info,
        },
    )


@nlp_router.post("/index/search/{project_title}")
async def search_index(
    request: Request,
    project_title: str,
    search_request: SearchRequest,
    db_client=Depends(get_db_client),
):
    project_repo = ProjectRepository(
        db_client=db_client,
        app_settings=request.app.app_settings,
    )
    project = await project_repo.get_project_or_create_new(project_title)
    if not project:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"message": ResponseMessagesEnum.PROJECT_NOT_FOUND.value},
        )
    nlp_controller = NLPController(
        vector_client=request.app.vector_db_provider,
        generator_client=request.app.generation_llm_provider,
        embedder_client=request.app.embedding_llm_provider,
        app_settings=request.app.app_settings,
        template_parser=request.app.template_parser,
    )
    search_result = await nlp_controller.search_vdb_index(
        project, search_request.query, search_request.limit
    )
    if not search_result:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={
                "message": ResponseMessagesEnum.PROJECT_VDB_INDEX_SEARCH_NOT_FOUND.value
            },
        )
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "message": ResponseMessagesEnum.PROJECT_VDB_INDEX_SEARCH_SUCCESS.value,
            "results": search_result,
        },
    )


@nlp_router.post("/index/answer/{project_title}")
async def rag_answer(
    request: Request,
    project_title: str,
    search_request: SearchRequest,
    db_client=Depends(get_db_client),
):
    project_repo = ProjectRepository(
        db_client=db_client,
        app_settings=request.app.app_settings,
    )
    project = await project_repo.get_project_or_create_new(project_title)
    if not project:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"message": ResponseMessagesEnum.PROJECT_NOT_FOUND.value},
        )

    nlp_controller = NLPController(
        vector_client=request.app.vector_db_provider,
        generator_client=request.app.generation_llm_provider,
        embedder_client=request.app.embedding_llm_provider,
        app_settings=request.app.app_settings,
        template_parser=request.app.template_parser,
    )

    rag_response = await nlp_controller.response_to_rag_query(
        project, search_request.query, search_request.limit
    )
    if rag_response == "GENERATION_FAILED":
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "message": ResponseMessagesEnum.PROJECT_VDB_INDEX_RAG_ANSWER_FAILED.value
            },
        )
    if not rag_response:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={
                "message": ResponseMessagesEnum.PROJECT_VDB_INDEX_RAG_ANSWER_NOT_FOUND.value
            },
        )
    answer, full_prompt, chat_history = rag_response
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "message": ResponseMessagesEnum.PROJECT_VDB_INDEX_RAG_ANSWER_SUCCESS.value,
            "answer": answer,
            "full_prompt": full_prompt,
            "chat_history": chat_history,
        },
    )
