import pytest
from unittest.mock import patch, MagicMock
from app.agents.matching_agent import evaluate_match
from app.db.models.resume import Resume
from app.db.models.job import Job

# Aditya M's Golden Resume mock data
GOLDEN_RESUME_DATA = {
    "name": "Aditya M",
    "email": "aditya@email.com",
    "phone": "555-0000",
    "location": "India",
    "linkedin": "https://linkedin.com/in/adityam",
    "github": "https://github.com/adityam",
    "skills": ["Python", "Machine Learning", "Generative AI", "FastAPI", "SQLAlchemy", "PostgreSQL"],
    "education": [
        {
            "institution": "Malnad College of Engineering",
            "degree": "Bachelor of Engineering in Information Science and Engineering",
            "start_date": "August 2022",
            "end_date": "June 2026",
            "gpa": "7.5"
        }
    ],
    "experience": [],
    "projects": [
        {
            "name": "AI Job Agent",
            "description": "Built an autonomous job search platform.",
            "technologies": ["Python", "FastAPI", "LLMs"]
        }
    ]
}

# Mock Job Data for an AI Engineer
MOCK_JOB_DATA = {
    "title": "AI Engineer",
    "company": "NextGen AI",
    "location": "Remote",
    "required_skills": ["Python", "Machine Learning", "FastAPI"],
    "preferred_skills": ["Generative AI", "Docker"],
    "responsibilities": ["Build AI pipelines"],
    "experience_requirements": "0-2 years",
    "education_requirements": "Bachelor's degree in CS or related field",
    "keywords": ["AI", "Python", "ML"]
}

@pytest.fixture
def mock_llm_provider():
    with patch("app.core.llm_provider.LLMFactory.get_provider") as mock_get_provider:
        mock_provider = MagicMock()
        mock_get_provider.return_value = mock_provider
        yield mock_provider

@pytest.fixture
def mock_embeddings():
    with patch("app.agents.matching_agent.get_embeddings") as mock_get_embeddings:
        mock_emb = MagicMock()
        # Return dummy vectors of length 3 for cosine similarity calculation
        mock_emb.embed_query.side_effect = [[1.0, 0.0, 0.0], [0.8, 0.6, 0.0]]
        mock_get_embeddings.return_value = mock_emb
        yield mock_emb

def test_semantic_matching_engine(mock_llm_provider, mock_embeddings):
    # Mock LLM Match Breakdown Response
    mock_llm_breakdown = MagicMock()
    mock_llm_breakdown.skill_match_score = 38.0
    mock_llm_breakdown.experience_match_score = 20.0
    mock_llm_breakdown.education_match_score = 10.0
    mock_llm_breakdown.keyword_match_score = 14.0
    mock_llm_breakdown.missing_skills = ["Docker"]
    mock_llm_breakdown.strength_areas = ["Python", "Machine Learning"]
    mock_llm_breakdown.weak_areas = ["Experience"]
    mock_llm_breakdown.keyword_coverage = 90.0
    mock_llm_breakdown.ats_readiness = "High"
    mock_llm_breakdown.education_match = True
    mock_llm_breakdown.experience_match = True

    mock_llm_provider.generate_structured_output.return_value = mock_llm_breakdown
    
    # Create mock Resume and Job objects
    mock_resume = Resume(id=1, user_id=1, parsed_data=GOLDEN_RESUME_DATA)
    mock_job = Job(id=1, parsed_data=MOCK_JOB_DATA)
    
    match_response = evaluate_match(mock_resume, mock_job, provider_name="openai")
    
    # Assertions
    assert match_response is not None
    assert match_response.resume_id == 1
    assert match_response.job_id == 1
    
    # Check if the final score calculated correctly:
    # 38 + 20 + 10 + 14 + semantic_score
    # With dummy vectors [1,0,0] and [0.8, 0.6, 0], dot product is 0.8
    # Semantic score max is 15. 0.8 * 15 = 12.0
    # Expected final score: 38 + 20 + 10 + 14 + 12 = 94.0
    assert match_response.final_match_score == 94.0
    assert match_response.score_breakdown.semantic_similarity_score == 12.0
    assert match_response.education_match is True
    assert "Docker" in match_response.missing_skills
