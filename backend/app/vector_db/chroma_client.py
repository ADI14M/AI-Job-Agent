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

from app.services.ai_service import ai_service

# Initialize OpenAI Embeddings for Vector generation
def get_embeddings():
    return ai_service.get_embeddings()

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

def get_job_descriptions_collection():
    return chroma_client.get_or_create_collection(
        name="job_descriptions",
        metadata={"hnsw:space": "cosine"}
    )

def get_career_memory_collection():
    return chroma_client.get_or_create_collection(
        name="career_memory",
        metadata={"hnsw:space": "cosine"}
    )

def get_company_memory_collection():
    return chroma_client.get_or_create_collection(
        name="company_memory",
        metadata={"hnsw:space": "cosine"}
    )

def get_application_memory_collection():
    return chroma_client.get_or_create_collection(
        name="application_memory",
        metadata={"hnsw:space": "cosine"}
    )
