from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional
import os
from dotenv import load_dotenv

# Load .env into os.environ so external libraries like OpenAI/LangChain can access it
load_dotenv()

class Settings(BaseSettings):
    PROJECT_NAME: str = "AI-Job-Agent"
    API_V1_STR: str = "/api/v1"
    
    # Security
    SECRET_KEY: str = "supersecretkey_please_change_in_production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7 # 7 days
    
    # PostgreSQL Database
    POSTGRES_SERVER: str = "localhost"
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "postgres"
    POSTGRES_DB: str = "ai_job_agent"
    POSTGRES_PORT: str = "5432"
    
    # ── LLM Provider ─────────────────────────────────────────────────────
    USE_OLLAMA: bool = True

    # Ollama settings (used when USE_OLLAMA=True)
    OLLAMA_BASE_URL: str = "http://localhost:11434/v1"
    OLLAMA_API_KEY: str = "ollama"          # Required by client, ignored by Ollama
    LLM_MODEL: str = "qwen2.5:7b"         # Best model for M5 24GB
    FAST_LLM_MODEL: str = "llama3.2:3b"    # Fast model for simple/routing tasks
    EMBEDDING_MODEL: str = "nomic-embed-text"

    # OpenAI settings (used when USE_OLLAMA=False)
    OPENAI_API_KEY: str = ""
    OPENAI_LLM_MODEL: str = "gpt-4o-mini"
    OPENAI_EMBEDDING_MODEL: str = "text-embedding-3-small"

    @property
    def active_llm_model(self) -> str:
        return self.LLM_MODEL if self.USE_OLLAMA else self.OPENAI_LLM_MODEL

    @property
    def active_embedding_model(self) -> str:
        return self.EMBEDDING_MODEL if self.USE_OLLAMA else self.OPENAI_EMBEDDING_MODEL
    
    # Environment Explicit Overrides
    DATABASE_URL: str = "sqlite:///./jobagent.db"
    CHROMA_PATH: str = "./chroma_db"
    
    @property
    def SQLALCHEMY_DATABASE_URI(self) -> str:
        return self.DATABASE_URL

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

settings = Settings()
