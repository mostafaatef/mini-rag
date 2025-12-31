APP_NAME="mini-RAG"
APP_VERSION="0.1"
FILE_ALLOWED_TYPES=["text/plain", "application/pdf"]
FILE_MAX_SIZE=10
FILE_CHUNK_SIZE=1000

OPENAI_API_KEY=""
COHERE_API_KEY="ytFNfgLq9dgKbHdPTAwmpAoYgyKBftZXhv2tDvUh"   #Production
#COHERE_API_KEY="6S1DSHEvOEYg9Nb1ldA5Yi3y8wChMqLJSbITHLth"  #trial
GOOGLE_API_KEY="AIzaSyA3kpGeznCyttJu0TubiC-C31nRnDHD-6I"
#OLLAMA_BASE_URL="http://localhost:11434/v1/"    #Local
OLLAMA_BASE_URL="https://cispadane-eva-autophytically.ngrok-free.dev/v1/"  #Colab

OPENAI_API_URL = ""

# ==Backends==
    ##Generation
GENERATION_BACKEND_LLM_LITERAL = ["OPENAI","OLLAMA","COHERE","COHERE"]
GENERATION_BACKEND_LLM = "COHERE"

    ##Emdedding
EMBEDDING_BACKEND_LLM_LITERAL = ["COHERE","OLLAMA","GOOGLE","OPENAI" ]
EMBEDDING_BACKEND_LLM = "COHERE"


# ==Generation Models==
GENERATION_MODEL_ID ="command-a-03-2025"    #COHERE
#GENERATION_MODEL_ID ="gpt-3.5-turbo"   #OPENAI
#GENERATION_MODEL_ID = "qwen2.5:3b-instruct-q3_k_s"  #OLLAMA
#GENERATION_MODEL_ID="gemma2:9b-instruct-q5_0"    # OLLAMA on Colab
#GENERATION_MODEL_ID ="gemini-flash-latest"  #GOOGLE
#GENERATION_MODEL_ID ="gemini-pro-latest"   #GOOGLE

# ==Embedding Models==
    ##COHERE Embedding Models
#EMBEDDING_MODEL_ID ="embed-multilingual-light-v3.0"
#EMBEDDING_MODEL_SIZE ="384"
EMBEDDING_MODEL_ID ="embed-multilingual-v3.0"
EMBEDDING_MODEL_SIZE ="1024"
    ##Google Embedding
#EMBEDDING_MODEL_ID = "models/text-embedding-004"
#EMBEDDING_MODEL_SIZE ="768"
    ##OLLAMA Embedding
#EMBEDDING_MODEL_ID = "nomic-embed-text"
#EMBEDDING_MODEL_SIZE = "768"

INPUT_MAX_CHARACTERS=1024
GENERATION_MAX_OUTPUT_TOKENS=200
GENERATION_TEMPERATURE=0.1

# ===================Backend DB==========================
DATABASE_TYPE_LITERAL = ["NOSQL","SQL"]
DATABASE_TYPE="SQL"

# ===================Mongo DB====================
MONGODB_URL="mongodb://localhost:27007"
MONGODB_DB="mini_rag"

# ===================Postgres====================
POSTGRES_USERNAME="minirag"
POSTGRES_PASSWORD="minirag"
POSTGRES_HOST="localhost"
POSTGRES_PORT=5432
POSTGRES_MAIN_DATABASE="mini_rag"


# ===================Vector DB====================
VECTOR_DB_BACKEND_LITERAL = ["QDRANT","PGVECTOR"]
VECTOR_DB_BACKEND="QDRANT"
VECTOR_DB_DISTANCE_METHOD ="COSINE"

VECTOR_QDRANT_DB_PATH="qdrant_db"
VECTOR_POSTGRES_DB_URL="postgresql://minirag:minirag@localhost:5432/mini_rag"
VECTOR_POSTGRES_INDEX_CREATION_THRESHOLD= 100 #1000 is more optimal

# ===================Template Config====================
DEFAULT_LANG = "ar"
