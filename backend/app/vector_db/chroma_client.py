import chromadb
from chromadb.config import Settings
import os
from langchain_openai import OpenAIEmbeddings

from app.core.config import settings

# Initialize ChromaDB Client
chroma_client = chromadb.PersistentClient(
    path=settings.CHROMA_PATH,
    settings=Settings(allow_reset=True, anonymized_telemetry=False)
)

# Initialize OpenAI Embeddings for Vector generation
def get_embeddings():
    if settings.USE_OLLAMA:
        return OpenAIEmbeddings(
            model=settings.active_embedding_model,
            openai_api_key=settings.OLLAMA_API_KEY,
            openai_api_base=settings.OLLAMA_BASE_URL
        )
    return OpenAIEmbeddings(
        model=settings.active_embedding_model,
        openai_api_key=settings.OPENAI_API_KEY
    )

# Create or get Resume Collection
def get_resume_collection():
    return chroma_client.get_or_create_collection(
        name="resumes",
        metadata={"hnsw:space": "cosine"} # Use cosine similarity
    )

def get_job_collection():
    return chroma_client.get_or_create_collection(
        name="jobs",
        metadata={"hnsw:space": "cosine"}
    )
