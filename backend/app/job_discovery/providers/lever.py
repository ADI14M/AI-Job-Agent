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

class LeverProvider(BaseJobProvider):
    def __init__(self):
        self.targets = self._load_targets()

    def _load_targets(self) -> List[str]:
        target_file = os.path.join(os.path.dirname(__file__), "..", "company_targets.json")
        try:
            with open(target_file, "r") as f:
                data = json.load(f)
                return data.get("lever", [])
        except Exception as e:
            system_logger.error(f"Failed to load lever targets: {e}")
            return []

    @property
    def provider_name(self) -> str:
        return "Lever"

    def search_jobs(self, query: str, location: str, limit: int, **kwargs) -> List[DiscoveredJob]:
        import concurrent.futures
        import random
        
        jobs = []
        targets = list(self.targets)
        random.shuffle(targets)
        
        def fetch_company(company: str) -> List[DiscoveredJob]:
            company_jobs = []
            try:
                url = f"https://api.lever.co/v0/postings/{company}?mode=json"
                response = requests.get(url, timeout=5)
                if response.status_code == 200:
                    data = response.json()
                    for job_data in data:
                        title = job_data.get("text", "")
                        categories = job_data.get("categories", {})
                        job_loc = categories.get("location", "")
                        
                        if query and query.lower() not in title.lower():
                            continue
                        if location and location.lower() not in job_loc.lower():
                            continue
                            
                        description = html.unescape(job_data.get("descriptionPlain", ""))
                        if not description:
                            description = job_data.get("description", "")
                        
                        company_jobs.append(DiscoveredJob(
                            title=title,
                            company=company.capitalize(),
                            location=job_loc,
                            employment_type=categories.get("commitment", "Full-time"),
                            salary="Unknown",
                            experience="Unknown",
                            description=description,
                            skills=[], 
                            url=job_data.get("hostedUrl", ""),
                            source="Lever",
                            posted_date=datetime.datetime.fromtimestamp(job_data.get("createdAt", 0)/1000.0).isoformat() if job_data.get("createdAt") else datetime.datetime.utcnow().isoformat(),
                            company_logo=None,
                            remote="remote" in job_loc.lower()
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

ProviderRegistry.register(LeverProvider())
