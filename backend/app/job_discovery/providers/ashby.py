import requests
import json
import os
import datetime
import html
from typing import List
from app.job_discovery.base_provider import BaseJobProvider
from app.job_discovery.provider_registry import ProviderRegistry
from app.job_discovery.models import DiscoveredJob
from app.core.logger import system_logger

class AshbyProvider(BaseJobProvider):
    def __init__(self):
        self.targets = self._load_targets()

    def _load_targets(self) -> List[str]:
        target_file = os.path.join(os.path.dirname(__file__), "..", "company_targets.json")
        try:
            with open(target_file, "r") as f:
                data = json.load(f)
                return data.get("ashby", [])
        except Exception as e:
            system_logger.error(f"Failed to load ashby targets: {e}")
            return []

    @property
    def provider_name(self) -> str:
        return "Ashby"

    def search_jobs(self, query: str, location: str, limit: int, **kwargs) -> List[DiscoveredJob]:
        import concurrent.futures
        import random
        
        jobs = []
        targets = list(self.targets)
        random.shuffle(targets)
        
        def fetch_company(company: str) -> List[DiscoveredJob]:
            company_jobs = []
            try:
                url = "https://jobs.ashbyhq.com/api/non-user-graphql?op=ApiJobBoardWithTeams"
                payload = {
                    "operationName": "ApiJobBoardWithTeams",
                    "variables": {"organizationHostedJobsPageName": company},
                    "query": "query ApiJobBoardWithTeams($organizationHostedJobsPageName: String!) { jobBoard: jobBoardWithTeams(organizationHostedJobsPageName: $organizationHostedJobsPageName) { jobPostings { id title locationName isRemote employmentType publishedAt jobBoardUrl descriptionHtml } } }"
                }
                
                response = requests.post(url, json=payload, timeout=5)
                if response.status_code == 200:
                    data = response.json()
                    job_board = data.get("data", {}).get("jobBoard", {})
                    if job_board:
                        for job_data in job_board.get("jobPostings", []):
                            title = job_data.get("title", "")
                            job_loc = job_data.get("locationName", "")
                            
                            if query and query.lower() not in title.lower():
                                continue
                            if location and location.lower() not in job_loc.lower():
                                continue
                                
                            description = html.unescape(job_data.get("descriptionHtml", ""))
                            if not description:
                                description = ""
                            
                            company_jobs.append(DiscoveredJob(
                                title=title,
                                company=company.capitalize(),
                                location=job_loc,
                                employment_type=job_data.get("employmentType", "Full-time"),
                                salary="Unknown",
                                experience="Unknown",
                                description=description,
                                skills=[], 
                                url=job_data.get("jobBoardUrl", ""),
                                source="Ashby",
                                posted_date=job_data.get("publishedAt", datetime.datetime.utcnow().isoformat()),
                                company_logo=None,
                                remote=job_data.get("isRemote", False)
                            ))
            except Exception as e:
                pass
            return company_jobs

        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            future_to_company = {executor.submit(fetch_company, c): c for c in targets}
            for future in concurrent.futures.as_completed(future_to_company):
                if len(jobs) >= limit:
                    break
                try:
                    res = future.result()
                    jobs.extend(res)
                    if len(jobs) >= limit:
                        jobs = jobs[:limit]
                        break
                except Exception:
                    pass
                
        return jobs

ProviderRegistry.register(AshbyProvider())
