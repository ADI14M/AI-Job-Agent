from typing import Type, TypeVar, Optional, Any
from pydantic import BaseModel
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from app.core.config import settings
from app.core.logger import ai_logger
from app.utils.json_utils import extract_json_from_text

T = TypeVar("T", bound=BaseModel)

class AIService:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(AIService, cls).__new__(cls)
            cls._instance._initialize()
        return cls._instance

    def _initialize(self):
        """Initializes LangChain OpenAI wrappers pointing to local Ollama."""
        ai_logger.info(f"Initializing AIService with Chat model {settings.CHAT_MODEL} and Embed model {settings.EMBED_MODEL}")
        
        self.chat_llm = ChatOpenAI(
            model=settings.CHAT_MODEL,
            temperature=settings.TEMPERATURE,
            api_key=settings.OLLAMA_API_KEY,
            base_url=settings.OLLAMA_BASE_URL,
            max_retries=2
        )
        
        self.fast_llm = ChatOpenAI(
            model=settings.FAST_MODEL,
            temperature=settings.TEMPERATURE,
            api_key=settings.OLLAMA_API_KEY,
            base_url=settings.OLLAMA_BASE_URL,
            max_retries=2
        )
        
        self.embeddings = OpenAIEmbeddings(
            model=settings.EMBED_MODEL,
            api_key=settings.OLLAMA_API_KEY,
            base_url=settings.OLLAMA_BASE_URL
        )

    def generate_text(self, prompt: str, use_fast_model: bool = False) -> str:
        llm = self.fast_llm if use_fast_model else self.chat_llm
        try:
            ai_logger.info(f"Generating text using {'fast' if use_fast_model else 'chat'} model.")
            response = llm.invoke(prompt)
            return response.content
        except Exception as e:
            ai_logger.error(f"Text generation failed: {e}")
            raise e

    def generate_structured_output(self, prompt: str, schema: Type[T], use_fast_model: bool = False) -> Optional[T]:
        llm = self.fast_llm if use_fast_model else self.chat_llm
        try:
            ai_logger.info(f"Generating structured output ({schema.__name__})")
            
            # Langchain native structured output
            structured_llm = llm.with_structured_output(schema)
            return structured_llm.invoke(prompt)
        except Exception as e:
            ai_logger.warning(f"Native structured output failed, falling back to JSON parsing: {e}")
            # Fallback: prompt for JSON and parse manually
            fallback_prompt = prompt + "\n\nCRITICAL: Respond ONLY with valid JSON matching the schema."
            try:
                response = llm.invoke(fallback_prompt)
                extracted_json = extract_json_from_text(response.content)
                if extracted_json:
                    return schema(**extracted_json)
                else:
                    raise ValueError("Failed to extract valid JSON from response.")
            except Exception as fallback_err:
                ai_logger.error(f"Fallback structured output failed: {fallback_err}")
                raise fallback_err

    def get_embeddings(self) -> OpenAIEmbeddings:
        """Returns the configured embeddings object (used by ChromaDB)."""
        return self.embeddings

# Singleton instance
ai_service = AIService()
