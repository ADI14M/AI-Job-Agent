from app.vector_db.chroma_client import get_resume_collection
from app.services.ai_service import ai_service
from app.core.logger import system_logger
from pydantic import BaseModel, Field
import numpy as np

class LLMMatchResult(BaseModel):
    match_score: int = Field(..., description="A score from 0 to 100 representing the semantic match")

class JobMatcher:
    @staticmethod
    def compute_match_score(job_text: str, user_id: int) -> float:
        """
        Computes cosine similarity against the user's latest resume in ChromaDB, 
        and uses an LLM to rerank the score.
        Returns a percentage score (0-100).
        """
        try:
            resume_collection = get_resume_collection()
            
            # Find user's resumes
            results = resume_collection.get(
                where={"user_id": user_id},
                include=["embeddings", "documents"]
            )
            
            if not results or len(results.get('embeddings', [])) == 0:
                return 0.0
                
            # Get the first resume embedding (assume latest)
            resume_emb = np.array(results['embeddings'][0])
            resume_text = results['documents'][0] if results.get('documents') else ""
            
            # Embed the job description
            embeddings_model = ai_service.get_embeddings()
            job_emb = np.array(embeddings_model.embed_query(job_text))
            
            # Cosine similarity
            similarity = np.dot(resume_emb, job_emb) / (np.linalg.norm(resume_emb) * np.linalg.norm(job_emb))
            base_score_percent = max(0.0, min(100.0, (similarity + 1) * 50))
            
            # Real LLM Reranking
            if base_score_percent > 30.0 and resume_text:  # Only rerank if there's a baseline match
                prompt = f"""
                You are an expert technical recruiter. Evaluate the fit between this resume and job description.
                Provide a final match score from 0 to 100 based on semantic skill requirements, seniority, and domain match.
                
                Resume:
                {resume_text[:3000]}
                
                Job Description:
                {job_text[:3000]}
                """
                try:
                    llm_result = ai_service.generate_structured_output(prompt, LLMMatchResult, use_fast_model=True)
                    if llm_result:
                        # Blend the vector score and LLM score (e.g. 30% vector, 70% LLM)
                        final_score = (base_score_percent * 0.3) + (llm_result.match_score * 0.7)
                        return round(final_score, 2)
                except Exception as e:
                    system_logger.error(f"LLM reranking failed, falling back to base score: {e}")
                    
            return round(base_score_percent, 2)
            
        except Exception as e:
            system_logger.error(f"Failed to compute match score: {e}")
            return 0.0
