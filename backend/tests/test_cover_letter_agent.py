import pytest
from unittest.mock import patch, MagicMock
from app.agents.cover_letter_agent import generate_cover_letter
from app.db.models.resume import Resume
from app.db.models.job import Job

GOLDEN_RESUME_DATA = {
    "name": "Aditya M",
    "skills": ["Python", "FastAPI"]
}

MOCK_JOB_DATA = {
    "title": "Backend Engineer",
    "company": "TechCorp",
    "required_skills": ["Python", "FastAPI"]
}

@pytest.fixture
def mock_llm_provider():
    with patch("app.core.llm_provider.LLMFactory.get_provider") as mock_get_provider:
        mock_provider = MagicMock()
        mock_get_provider.return_value = mock_provider
        yield mock_provider

def test_generate_cover_letter(mock_llm_provider):
    mock_cl_data = MagicMock()
    mock_cl_data.content = "Dear Hiring Manager at TechCorp, I am Aditya M..."
    
    mock_llm_provider.generate_structured_output.return_value = mock_cl_data
    
    mock_resume = Resume(id=1, user_id=1, parsed_data=GOLDEN_RESUME_DATA)
    mock_job = Job(id=1, parsed_data=MOCK_JOB_DATA)
    
    cl = generate_cover_letter(mock_resume, mock_job, provider_name="openai")
    
    assert cl is not None
    assert "TechCorp" in cl.content
