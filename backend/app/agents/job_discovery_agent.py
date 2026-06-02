import logging
import uuid
from typing import List
from abc import ABC, abstractmethod
from app.schemas.job_discovery import DiscoveredJob

logger = logging.getLogger(__name__)

class BaseJobCollector(ABC):
    @abstractmethod
    def search_jobs(self, query: str, location: str, limit: int) -> List[DiscoveredJob]:
        pass

class MockLinkedInCollector(BaseJobCollector):
    def search_jobs(self, query: str, location: str, limit: int) -> List[DiscoveredJob]:
        # Simulated extraction
        jobs = []
        for i in range(limit):
            jobs.append(DiscoveredJob(
                title=f"{query} Engineer - Level {i}",
                company="Tech Innovators LLC",
                location=location,
                salary="$120,000 - $150,000",
                description="We are looking for an experienced engineer with skills in Python and Cloud computing.",
                apply_url=f"https://linkedin.com/jobs/view/{uuid.uuid4()}",
                platform="linkedin"
            ))
        return jobs

class MockIndeedCollector(BaseJobCollector):
    def search_jobs(self, query: str, location: str, limit: int) -> List[DiscoveredJob]:
        # Simulated extraction
        jobs = []
        for i in range(limit):
            jobs.append(DiscoveredJob(
                title=f"Senior {query} Developer",
                company="DataSystems Inc",
                location=location,
                salary=None,
                description="Strong background in fastAPI and databases required.",
                apply_url=f"https://indeed.com/viewjob?jk={uuid.uuid4()}",
                platform="indeed"
            ))
        return jobs

class JobDiscoveryAgent:
    def __init__(self):
        self.collectors = {
            "linkedin": MockLinkedInCollector(),
            "indeed": MockIndeedCollector()
        }

    def run_discovery(self, query: str, location: str, platforms: List[str], limit: int) -> List[DiscoveredJob]:
        all_jobs = []
        for platform in platforms:
            collector = self.collectors.get(platform.lower())
            if collector:
                try:
                    platform_limit = max(1, limit // len(platforms))
                    jobs = collector.search_jobs(query, location, platform_limit)
                    all_jobs.extend(jobs)
                except Exception as e:
                    logger.error(f"Error collecting from {platform}: {e}")
        return all_jobs
