from abc import ABC, abstractmethod
from typing import List, Dict, Any
from app.job_discovery.models import DiscoveredJob

class BaseJobProvider(ABC):
    @property
    @abstractmethod
    def provider_name(self) -> str:
        """The identifier of the provider (e.g., 'linkedin')."""
        pass

    @abstractmethod
    def search_jobs(self, query: str, location: str, limit: int, **kwargs) -> List[DiscoveredJob]:
        """
        Search for jobs based on the query and location.
        Returns a list of DiscoveredJob objects adhering to the standardized schema.
        """
        pass
