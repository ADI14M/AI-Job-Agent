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
    OLLAMA_BASE_URL: str = "http://localhost:11434/v1"
    OLLAMA_API_KEY: str = "ollama"
    CHAT_MODEL: str = "qwen2.5:7b"
    FAST_MODEL: str = "llama3.2:3b"
    EMBED_MODEL: str = "nomic-embed-text"
    TEMPERATURE: float = 0.0

    @property
    def active_llm_model(self) -> str:
        return self.CHAT_MODEL

    @property
    def active_embedding_model(self) -> str:
        return self.EMBED_MODEL

    # ── Paths & Environment ──────────────────────────────────────────────
    DATABASE_URL: str = "sqlite:///./jobagent.db"
    CHROMA_PATH: str = "./chroma_db"
    PROMPTS_FOLDER: str = "app/prompts"
    GENERATED_FOLDER: str = "app/generated"
    PLAYWRIGHT_HEADLESS: bool = False
    
    @property
    def SQLALCHEMY_DATABASE_URI(self) -> str:
        return self.DATABASE_URL

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

settings = Settings()
