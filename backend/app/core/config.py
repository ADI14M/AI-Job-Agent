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
    
    # External APIs
    OPENAI_API_KEY: Optional[str] = None
    
    # Environment Explicit Overrides
    DATABASE_URL: Optional[str] = None
    CHROMA_DB_DIR: str = "./chroma_data"
    
    @property
    def SQLALCHEMY_DATABASE_URI(self) -> str:
        # Default to SQLite for easy local execution without Postgres/Docker
        db_url = self.DATABASE_URL
        if db_url:
            return db_url
        return "sqlite:///./job_agent.db"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

settings = Settings()
