import json
from typing import Optional
from app.schemas.matching import MatchingResponse, MatchScoreDetails
from app.services.ai_service import ai_service
from app.utils.prompt_loader import PromptLoader
from app.core.logger import system_logger
from app.db.models.resume import Resume
from app.db.models.job import Job
from app.vector_db.chroma_client import get_embeddings
from pydantic import BaseModel, Field

# Temporary schema for LLM structured output without the semantic score
class LLMMatchBreakdown(BaseModel):
    skill_match_score: float = Field(..., description="Score out of 40")
    experience_match_score: float = Field(..., description="Score out of 20")
    education_match_score: float = Field(..., description="Score out of 10")
    keyword_match_score: float = Field(..., description="Score out of 15")
    missing_skills: list[str]
    strength_areas: list[str]
    weak_areas: list[str]
    keyword_coverage: float = Field(..., description="Percentage as a float (0-100)")
    ats_readiness: str = Field(..., description="'High', 'Medium', or 'Low'")
    education_match: bool
    experience_match: bool

def calculate_semantic_similarity(resume_text: str, job_text: str) -> float:
    try:
        embeddings_model = get_embeddings()
        res_emb = embeddings_model.embed_query(resume_text)
        job_emb = embeddings_model.embed_query(job_text)
        
        import numpy as np
        vec1 = np.array(res_emb)
        vec2 = np.array(job_emb)
        similarity = np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))
        
        score = max(0.0, min(15.0, similarity * 15.0))
        return round(score, 2)
    except Exception as e:
        system_logger.error(f"Semantic similarity calculation failed: {e}")
        return 0.0

def evaluate_match(resume: Resume, job: Job) -> Optional[MatchingResponse]:
    semantic_score = calculate_semantic_similarity(
        resume_text=json.dumps(resume.parsed_data) if resume.parsed_data else resume.raw_text,
        job_text=json.dumps(job.parsed_data) if job.parsed_data else job.raw_text
    )
    
    prompt = PromptLoader.load(
        "job_match.txt", 
        resume_data=json.dumps(resume.parsed_data), 
        job_data=json.dumps(job.parsed_data)
    )
    
    try:
        llm_response = ai_service.generate_structured_output(prompt, LLMMatchBreakdown, use_fast_model=False)
        if not llm_response:
            raise ValueError("LLM returned None for matching breakdown.")
            
        final_score = (
            llm_response.skill_match_score +
            llm_response.experience_match_score +
            llm_response.education_match_score +
            llm_response.keyword_match_score +
            semantic_score
        )
        
        score_details = MatchScoreDetails(
            skill_match_score=llm_response.skill_match_score,
            experience_match_score=llm_response.experience_match_score,
            education_match_score=llm_response.education_match_score,
            keyword_match_score=llm_response.keyword_match_score,
            semantic_similarity_score=semantic_score
        )
        
        response = MatchingResponse(
            resume_id=resume.id,
            job_id=job.id,
            final_match_score=round(final_score, 2),
            score_breakdown=score_details,
            missing_skills=llm_response.missing_skills,
            strength_areas=llm_response.strength_areas,
            weak_areas=llm_response.weak_areas,
            keyword_coverage=llm_response.keyword_coverage,
            ats_readiness=llm_response.ats_readiness,
            education_match=llm_response.education_match,
            experience_match=llm_response.experience_match
        )
        
        return response

    except Exception as e:
        system_logger.error(f"Error during semantic matching: {e}")
        return None
