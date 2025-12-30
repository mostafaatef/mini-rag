from .BaseController import BaseController
from src.helpers.config import Settings
from src.models.schemes.mini_rag_db import Project
from src.models.schemes.mini_rag_db import Chunk
from src.stores.llm.templates.template_parser import TemplateParser
from typing import List
from src.stores.llm.LLMEnum import InputType
from bson import ObjectId
import logging
import uuid


class NLPController(BaseController):
    def __init__(
        self,
        vector_client: object,
        generator_client: object,
        embedder_client: object,
        app_settings: Settings,
        template_parser: TemplateParser,
    ):
        super().__init__(app_settings)

        self.vector_client = vector_client
        self.generator_client = generator_client
        self.embedder_client = embedder_client
        self.template_parser = template_parser
        self.app_settings = app_settings
        self.logger = logging.getLogger(__name__)

    def create_vdb_collection_name(self, project_id: str):
        if self.app_settings.VECTOR_DB_BACKEND == "PGVECTOR":
            return f"Vector_{project_id}".strip()
        return f"Collection_{project_id}".strip()

    async def reset_vdb_collection(self, project: Project):
        collection_name = self.create_vdb_collection_name(project.project_title)
        result = await self.vector_client.delete_collection(collection_name)
        return result

    async def get_vdb_collection_info(self, project: Project):
        collection_name = self.create_vdb_collection_name(project.project_title)
        result = await self.vector_client.get_collection_info(collection_name)
        return result

    async def search_vdb_index(self, project: Project, query: str, limit: int = 10):
        collection_name = self.create_vdb_collection_name(project.project_title)
        vectors = self.embedder_client.generate_embedding(query, InputType.QUERY.value)
        if not vectors or len(vectors) == 0:
            return None
        result = await self.vector_client.search_by_vector(
            collection_name=collection_name,
            vector=vectors,
            limit=limit,
        )
        if not result or len(result) == 0:
            return None
        return [item.dict() for item in result]

    def _sanitize_metadata(self, data):
        """Recursively sanitize metadata for JSON serialization."""
        import datetime

        if isinstance(data, dict):
            return {k: self._sanitize_metadata(v) for k, v in data.items()}
        elif isinstance(data, list):
            return [self._sanitize_metadata(i) for i in data]
        elif isinstance(data, (ObjectId, uuid.UUID, datetime.datetime, datetime.date)):
            return str(data)
        return data

    async def index_into_vdb(
        self, project: Project, chunks: List[Chunk], do_reset: bool = False
    ):
        collection_name = self.create_vdb_collection_name(project.project_title)

        texts = [chunk.chunk_content for chunk in chunks]
        metadata = [
            self._sanitize_metadata(chunk.dict(by_alias=True, exclude_none=True))
            for chunk in chunks
        ]
        self.logger.debug(
            f"Starting batch embedding generation for {len(texts)} chunks"
        )
        vectors = self.embedder_client.generate_embeddings(
            texts, InputType.DOCUMENT.value
        )
        if not vectors:
            self.logger.error("Failed to generate embeddings")
            return False

        await self.vector_client.create_collection(
            collection_name=collection_name,
            embedding_size=self.embedder_client.embedding_model_size,
            do_reset=do_reset,
        )

        is_inserted = await self.vector_client.insert_many(
            collection_name=collection_name,
            texts=texts,
            metadatas=metadata,
            vectors=vectors,
        )

        return is_inserted

    async def create_vdb_index(self, project: Project):
        collection_name = self.create_vdb_collection_name(project.project_title)
        # Only some providers (like PGVector) benefit from explicit index creation
        if hasattr(self.vector_client, "create_index"):
            await self.vector_client.create_index(collection_name)
        return True

    async def response_to_rag_query(
        self, project: Project, query: str, limit: int = 10
    ):
        # step 1, retrieve related indexed chunks
        retrieved_chunk_indices = await self.search_vdb_index(project, query, limit)
        if not retrieved_chunk_indices or len(retrieved_chunk_indices) == 0:
            return None
        # step 2, construct LLM prompot
        system_prompt = self.template_parser.get("RAG", "system_prompt")
        if isinstance(system_prompt, list):
            system_prompt = "\n".join(system_prompt)

        documents_prompt = "\n".join(
            [
                self.template_parser.get(
                    "RAG",
                    "document_prompt",
                    {
                        "document_no": idx + 1,
                        "document_content": self.generator_client.process_input(
                            doc.get("text")
                            or doc.get("payload", {}).get("text", "")
                            or ""
                        ),
                    },
                )
                for idx, doc in enumerate(retrieved_chunk_indices)
            ]
        )

        footer_prompt = self.template_parser.get(
            "RAG", "footer_prompt", {"query": query}
        )

        chat_history = [
            self.generator_client.construct_prompt(
                prompt=system_prompt,
                role=self.generator_client.enums.SYSTEM.value,
            )
        ]

        full_prompt = "\n\n".join(
            [
                f"User Question: {query}\n\nRelevant Documents:",
                documents_prompt,
                footer_prompt,
            ]
        )

        answer = self.generator_client.generate_response(
            query=full_prompt,
            chat_history=chat_history,
            max_output_tokens=2048,
            temperature=0.2,
        )
        if not answer:
            # Generation failed
            return "GENERATION_FAILED"
        return answer, full_prompt, chat_history
