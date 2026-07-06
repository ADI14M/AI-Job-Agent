from app.job_discovery.models import DiscoveredJob
import re

class JobNormalizer:
    @staticmethod
    def normalize(job: DiscoveredJob) -> DiscoveredJob:
        job.employment_type = JobNormalizer._normalize_employment_type(job.employment_type)
        job.remote = JobNormalizer._determine_remote(job.location, job.title, job.remote)
        job.salary = JobNormalizer._normalize_salary(job.salary)
        return job

    @staticmethod
    def _normalize_employment_type(emp_type: str) -> str:
        if not emp_type:
            return "Full-time"
        emp_type = emp_type.lower()
        if "contract" in emp_type:
            return "Contract"
        if "part" in emp_type:
            return "Part-time"
        if "intern" in emp_type:
            return "Internship"
        return "Full-time"

    @staticmethod
    def _determine_remote(location: str, title: str, is_remote: bool) -> bool:
        if is_remote:
            return True
        combined = f"{location or ''} {title or ''}".lower()
        return "remote" in combined or "anywhere" in combined

    @staticmethod
    def _normalize_salary(salary: str) -> str:
        if not salary:
            return "Not specified"
        # basic cleanup
        return re.sub(r'\s+', ' ', salary).strip()
