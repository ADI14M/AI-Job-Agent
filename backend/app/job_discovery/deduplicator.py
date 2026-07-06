import hashlib
from typing import List, Dict, Set
from rapidfuzz import fuzz
from app.job_discovery.models import DiscoveredJob
from app.db.models.job_discovery import JobDiscovery
from sqlalchemy.orm import Session
from app.core.logger import system_logger

class Deduplicator:
    def __init__(self, db: Session, similarity_threshold: float = 85.0):
        self.db = db
        self.similarity_threshold = similarity_threshold
        # Cache existing hashes for quick exact match lookup
        self.existing_hashes: Set[str] = {
            r[0] for r in self.db.query(JobDiscovery.hash).all()
        }
        # Pre-load existing jobs for fuzzy matching (could be memory intensive for large DBs, limit for now)
        self.existing_jobs = self.db.query(JobDiscovery.id, JobDiscovery.raw_json).order_by(JobDiscovery.id.desc()).limit(1000).all()

    @staticmethod
    def generate_hash(job: DiscoveredJob) -> str:
        unique_string = f"{job.title}|{job.company}|{job.location}|{job.description[:100]}"
        return hashlib.sha256(unique_string.lower().encode('utf-8')).hexdigest()

    def is_duplicate(self, job: DiscoveredJob) -> bool:
        job_hash = self.generate_hash(job)
        
        # 1. Exact Hash Match
        if job_hash in self.existing_hashes:
            return True

        # 2. Fuzzy Match (Title + Company) against recent jobs
        job_signature = f"{job.title} {job.company}".lower()
        for ej_id, ej_json in self.existing_jobs:
            ej_title = ej_json.get('title', '')
            ej_company = ej_json.get('company', '')
            ej_signature = f"{ej_title} {ej_company}".lower()
            
            score = fuzz.ratio(job_signature, ej_signature)
            if score >= self.similarity_threshold:
                system_logger.info(f"Fuzzy duplicate detected: '{job.title}' matched '{ej_title}' (Score: {score})")
                return True

        # If not duplicate, record hash temporarily to prevent intra-batch duplicates
        self.existing_hashes.add(job_hash)
        return False
