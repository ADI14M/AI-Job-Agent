import os
import logging
from abc import ABC, abstractmethod
from typing import Type, Any, TypeVar, Optional
from pydantic import BaseModel
from langchain_openai import ChatOpenAI
# from langchain_google_genai import ChatGoogleGenerativeAI
# from langchain_community.chat_models import ChatOllama

logger = logging.getLogger(__name__)

T = TypeVar("T", bound=BaseModel)

class BaseLLMProvider(ABC):
    @abstractmethod
    def generate_structured_output(self, prompt: str, schema: Type[T]) -> Optional[T]:
        pass

    @abstractmethod
    def generate_text(self, prompt: str) -> str:
        pass


class OpenAIProvider(BaseLLMProvider):
    def __init__(self, model_name: str = None, temperature: float = 0.0):
        from app.core.config import settings
        
        # Always use the globally active model setting
        model = settings.active_llm_model
        
        if settings.USE_OLLAMA:
            self.llm = ChatOpenAI(
                model=model, 
                temperature=temperature, 
                api_key=settings.OLLAMA_API_KEY, 
                base_url=settings.OLLAMA_BASE_URL
            )
        else:
            self.api_key = settings.OPENAI_API_KEY
            if not self.api_key:
                logger.warning("OPENAI_API_KEY is not set. OpenAI calls will fail.")
            self.llm = ChatOpenAI(model=model, temperature=temperature, api_key=self.api_key)

    def generate_structured_output(self, prompt: str, schema: Type[T]) -> Optional[T]:
        try:
            structured_llm = self.llm.with_structured_output(schema)
            return structured_llm.invoke(prompt)
        except Exception as e:
            logger.error(f"OpenAI structured output failed: {e}")
            raise e

    def generate_text(self, prompt: str) -> str:
        try:
            response = self.llm.invoke(prompt)
            return response.content
        except Exception as e:
            logger.error(f"OpenAI text generation failed: {e}")
            raise e


class OllamaProvider(BaseLLMProvider):
    def __init__(self, model_name: str = "llama3", temperature: float = 0.0):
        # Requires langchain-community and ollama installed locally
        from langchain_community.chat_models import ChatOllama
        self.llm = ChatOllama(model=model_name, temperature=temperature)
    
    def generate_structured_output(self, prompt: str, schema: Type[T]) -> Optional[T]:
        try:
            # Ollama doesn't natively support with_structured_output in all models as well as OpenAI,
            # but Langchain wraps it for json mode if supported, or we use a parser.
            structured_llm = self.llm.with_structured_output(schema)
            return structured_llm.invoke(prompt)
        except Exception as e:
            logger.error(f"Ollama structured output failed: {e}")
            raise e

    def generate_text(self, prompt: str) -> str:
        try:
            response = self.llm.invoke(prompt)
            return response.content
        except Exception as e:
            logger.error(f"Ollama text generation failed: {e}")
            raise e


class LLMFactory:
    @staticmethod
    def get_provider(provider_name: str = "openai", **kwargs) -> BaseLLMProvider:
        provider_name = provider_name.lower()
        if provider_name == "openai":
            return OpenAIProvider(**kwargs)
        elif provider_name == "ollama":
            return OllamaProvider(**kwargs)
        # Add Gemini etc. later
        else:
            raise ValueError(f"Unsupported LLM provider: {provider_name}")
