from enum import Enum


class LLMEnum(Enum):
    OPENAI = "OPENAI"
    COHERE = "COHERE"
    ANTHROPIC = "ANTHROPIC"
    GOOGLE = "GOOGLE"


class OpenAIEnum(Enum):
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


class CohereEnum(Enum):
    USER = "user"
    CHATBOT = "chatbot"
    SYSTEM = "system"
    DOCUMENT_INPUT_TYPE = "search_document"
    QUERY_INPUT_TYPE = "search_query"


class GoogleEnum(Enum):
    USER = "user"
    MODEL = "model"
    DOCUMENT_INPUT_TYPE = "retrieval_document"
    QUERY_INPUT_TYPE = "retrieval_query"


class InputType(Enum):
    DOCUMENT = "document"
    QUERY = "query"
