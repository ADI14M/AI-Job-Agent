from typing import List, Dict, Any
from sqlalchemy.orm import Session
from app.db.models.job_discovery import JobDiscovery
from app.job_discovery.provider_registry import ProviderRegistry
from app.job_discovery.normalizer import JobNormalizer
from app.job_discovery.deduplicator import Deduplicator
from app.job_discovery.matcher import JobMatcher
from app.vector_db.chroma_client import get_job_descriptions_collection
from app.services.ai_service import ai_service
from app.core.logger import system_logger
import uuid

class DiscoveryEngine:
    def __init__(self, db: Session, user_id: int):
        self.db = db
        self.user_id = user_id
        self.deduplicator = Deduplicator(db)
        self.chroma_collection = get_job_descriptions_collection()

    def run(self, query: str, location: str, providers: List[str], limit: int) -> Dict[str, Any]:
        results = {
            "summary": "Discovery complete",
            "total_found": 0,
            "duplicates_removed": 0,
            "new_jobs": 0,
            "matched_jobs": [],
            "provider_statuses": [],
            "errors": []
        }

        all_discovered = []
        provider_limit = max(1, limit // len(providers)) if providers else limit
        
        import concurrent.futures
        
        def run_provider(provider_name: str) -> Dict[str, Any]:
            status_entry = {
                "provider": provider_name,
                "status": "success",
                "reason": "OK",
                "response_code": 200,
                "jobs_found": 0,
                "jobs": []
            }
            try:
                provider = ProviderRegistry.get_provider(provider_name)
                system_logger.info(f"Provider {provider_name} started.")
                
                jobs = provider.search_jobs(query=query, location=location, limit=provider_limit)
                status_entry["jobs_found"] = len(jobs)
                status_entry["jobs"] = jobs
                
                system_logger.info(f"Provider {provider_name} finished. Found {len(jobs)} jobs.")
            except Exception as e:
                system_logger.error(f"Provider {provider_name} failed: {e}")
                status_entry["status"] = "error"
                status_entry["reason"] = str(e)
                status_entry["response_code"] = 500
            
            return status_entry

        with concurrent.futures.ThreadPoolExecutor(max_workers=len(providers)) as executor:
            future_to_provider = {executor.submit(run_provider, p): p for p in providers}
            for future in concurrent.futures.as_completed(future_to_provider):
                res = future.result()
                results["provider_statuses"].append({k: v for k, v in res.items() if k != "jobs"})
                results["total_found"] += res["jobs_found"]
                all_discovered.extend(res["jobs"])
                if res["status"] == "error":
                    results["errors"].append(res["reason"])

        # Pipeline: Normalize -> Deduplicate -> Embed -> Match -> Save
        for job in all_discovered:
            # 1. Normalize
            normalized_job = JobNormalizer.normalize(job)

            # 2. Deduplicate
            if self.deduplicator.is_duplicate(normalized_job):
                results["duplicates_removed"] += 1
                continue

            # 3. Match
            job_text = f"{normalized_job.title} {normalized_job.company} {normalized_job.description}"
            match_score = JobMatcher.compute_match_score(job_text, self.user_id)

            # 4. Save to Database
            job_hash = self.deduplicator.generate_hash(normalized_job)
            db_job = JobDiscovery(
                provider=normalized_job.source,
                hash=job_hash,
                raw_json=job.model_dump(),
                normalized_json=normalized_job.model_dump(),
                match_score=match_score,
                embedding_status="pending"
            )
            self.db.add(db_job)
            self.db.commit()
            self.db.refresh(db_job)

            # 5. Embed in ChromaDB
            try:
                self.chroma_collection.add(
                    documents=[job_text],
                    metadatas=[{
                        "company": normalized_job.company,
                        "title": normalized_job.title,
                        "source": normalized_job.source,
                        "location": normalized_job.location or "Unknown",
                        "remote": normalized_job.remote,
                        "database_id": db_job.id
                    }],
                    ids=[f"discovery_{db_job.id}_{uuid.uuid4()}"]
                )
                db_job.embedding_status = "completed"
                self.db.commit()
            except Exception as e:
                system_logger.error(f"Failed to embed job {db_job.id}: {e}")
                db_job.embedding_status = "failed"
                self.db.commit()

            results["new_jobs"] += 1
            # Add to response with DB ID and Match Score
            job_response = normalized_job.model_dump()
            job_response["id"] = db_job.id
            job_response["match_score"] = match_score
            results["matched_jobs"].append(job_response)

        # Sort matched jobs by score descending
        results["matched_jobs"].sort(key=lambda x: x.get("match_score", 0), reverse=True)
        
        system_logger.info(f"Discovery Engine complete. Found {results['total_found']}, new: {results['new_jobs']}, duplicates: {results['duplicates_removed']}")
        return results
