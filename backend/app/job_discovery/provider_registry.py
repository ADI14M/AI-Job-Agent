from typing import Dict, Type
from app.job_discovery.base_provider import BaseJobProvider
from app.core.logger import system_logger

class ProviderRegistry:
    _providers: Dict[str, BaseJobProvider] = {}

    @classmethod
    def register(cls, provider: BaseJobProvider):
        cls._providers[provider.provider_name.lower()] = provider
        system_logger.info(f"Registered Job Provider: {provider.provider_name}")

    @classmethod
    def get_provider(cls, name: str) -> BaseJobProvider:
        provider = cls._providers.get(name.lower())
        if not provider:
            raise ValueError(f"Provider {name} is not registered.")
        return provider

    @classmethod
    def get_all_providers(cls) -> Dict[str, BaseJobProvider]:
        return cls._providers
