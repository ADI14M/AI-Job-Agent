import logging
from typing import List, Dict
from app.db.models.resume import Resume
from app.db.models.job import Job
from app.schemas.job_ranking import JobRankResult

logger = logging.getLogger(__name__)

class JobRankingAgent:
    def __init__(self, weights: dict = None):
        # Default Weights
        self.weights = weights or {
            "match_score": 0.5,
            "ats_score": 0.3,
            "salary_score": 0.1,
            "location_score": 0.1
        }
        
    def _extract_salary_score(self, job: Job) -> float:
        # Mock salary parsing for ranking. 1.0 means high salary.
        return 0.8
        
    def _extract_location_score(self, job: Job, prefs: dict) -> float:
        # Mock location match against user preferences
        if prefs and prefs.get("remote_only") and job.parsed_data.get("remote", False):
            return 1.0
        return 0.5

    def rank_jobs(self, resume: Resume, jobs: List[Job], match_scores: Dict[int, float], ats_scores: Dict[int, float], preferences: dict = None) -> List[JobRankResult]:
        ranked = []
        for job in jobs:
            m_score = match_scores.get(job.id, 0.0)
            a_score = ats_scores.get(job.id, 0.0)
            s_score = self._extract_salary_score(job)
            l_score = self._extract_location_score(job, preferences)
            
            total = (m_score * self.weights["match_score"]) + \
                    (a_score * self.weights["ats_score"]) + \
                    (s_score * self.weights["salary_score"]) + \
                    (l_score * self.weights["location_score"])
                    
            ranked.append(JobRankResult(
                job_id=job.id,
                total_score=total,
                match_score=m_score,
                ats_score=a_score,
                salary_score=s_score,
                location_score=l_score,
                rank_reasoning=f"Ranked heavily by match ({m_score*100:.1f}%) and ATS score ({a_score*100:.1f}%)."
            ))
            
        # Sort descending
        ranked.sort(key=lambda x: x.total_score, reverse=True)
        return ranked
