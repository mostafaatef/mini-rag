from enum import Enum


class ResponseMessagesEnum(Enum):
    FILE_TYPE_NOT_ALLOWED = "file_type_not_allowed"
    FILE_SIZE_TOO_LARGE = "file_size_too_large"
    FILE_UPLOAD_SUCCESS = "file_upload_success"
    FILE_UPLOAD_FAILED = "file_upload_failed"
    FILE_PROCESSING_FAILED = "file_processing_failed"
    FILE_PROCESSING_SUCCESS = "file_processing_success"
    FILE_NOT_FOUND = "file_not_found"
    PROJECT_NOT_FOUND = "project_not_found"
    PROJECT_INDEX_PUSH_SUCCESS = "project_index_push_success"
    PROJECT_INDEX_PUSH_FAILED = "project_index_push_failed"
    CHUNK_NOT_FOUND = "chunk_not_found"
    PROJECT_VDB_INDEX_INFO_SUCCESS = "project_vdb_index_info_success"
    PROJECT_VDB_INDEX_INFO_FAILED = "project_vdb_index_info_failed"
    PROJECT_VDB_INDEX_SEARCH_SUCCESS = "project_vdb_index_search_success"
    PROJECT_VDB_INDEX_SEARCH_FAILED = "project_vdb_index_search_failed"
    PROJECT_VDB_INDEX_SEARCH_NOT_FOUND = "project_vdb_index_search_not_found"
    PROJECT_VDB_INDEX_RAG_ANSWER_SUCCESS = "project_vdb_index_rag_answer_success"
    PROJECT_VDB_INDEX_RAG_ANSWER_FAILED = "project_vdb_index_rag_answer_failed"
    PROJECT_VDB_INDEX_RAG_ANSWER_NOT_FOUND = "project_vdb_index_rag_answer_not_found"
