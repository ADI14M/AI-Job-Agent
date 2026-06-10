import chromadb
from chromadb.config import Settings
import os
from langchain_openai import OpenAIEmbeddings

from app.core.config import settings

# Initialize ChromaDB Client
chroma_client = chromadb.PersistentClient(
    path=settings.CHROMA_DB_DIR,
    settings=Settings(allow_reset=True, anonymized_telemetry=False)
)

# Initialize OpenAI Embeddings for Vector generation
def get_embeddings():
    return OpenAIEmbeddings(openai_api_key=os.getenv("OPENAI_API_KEY"))

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
