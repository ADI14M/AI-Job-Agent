import pytest
from unittest.mock import patch, MagicMock
from app.agents.resume_optimizer_agent import optimize_resume_for_role
from app.db.models.resume import Resume
from app.schemas.resume import ResumeParsedData

GOLDEN_RESUME_DATA = {
    "name": "Aditya M",
    "skills": ["Python", "FastAPI"],
    "experience": []
}

@pytest.fixture
def mock_llm_provider():
    with patch("app.core.llm_provider.LLMFactory.get_provider") as mock_get_provider:
        mock_provider = MagicMock()
        mock_get_provider.return_value = mock_provider
        yield mock_provider

def test_optimize_resume_for_role(mock_llm_provider):
    mock_optimized_data = ResumeParsedData(
        name="Aditya M",
        email=None,
        phone=None,
        location=None,
        linkedin=None,
        github=None,
        portfolio=None,
        summary="Optimized for AI Engineer",
        skills=["Python", "FastAPI"],
        education=[],
        experience=[],
        projects=[],
        certifications=[],
        achievements=[]
    )

    mock_llm_provider.generate_structured_output.return_value = mock_optimized_data
    
    mock_resume = Resume(id=1, user_id=1, parsed_data=GOLDEN_RESUME_DATA)
    
    optimized = optimize_resume_for_role(mock_resume, "AI Engineer", provider_name="openai")
    
    assert optimized is not None
    assert optimized.summary == "Optimized for AI Engineer"
    assert optimized.name == "Aditya M"
