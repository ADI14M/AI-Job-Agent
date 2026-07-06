from typing import List
from app.job_discovery.base_provider import BaseJobProvider
from app.job_discovery.provider_registry import ProviderRegistry
from app.job_discovery.models import DiscoveredJob

class GoogleJobsProvider(BaseJobProvider):
    @property
    def provider_name(self) -> str:
        return "GoogleJobs"

    def search_jobs(self, query: str, location: str, limit: int, **kwargs) -> List[DiscoveredJob]:
        return []

ProviderRegistry.register(GoogleJobsProvider())
