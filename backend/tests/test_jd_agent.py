import pytest
from unittest.mock import patch, MagicMock
from app.agents.jd_agent import process_and_store_job
from app.schemas.job import JobParsedData

MOCK_JD_TEXT = """
Backend Engineer at TechCorp
Location: Remote
Salary: $120k - $150k
Requirements:
- 5+ years of experience
- Strong Python, FastAPI, and PostgreSQL skills
- Experience with Docker and Kubernetes is preferred
Responsibilities:
- Build and maintain scalable APIs.
"""

@pytest.fixture
def mock_llm_provider():
    with patch("app.core.llm_provider.LLMFactory.get_provider") as mock_get_provider:
        mock_provider = MagicMock()
        mock_get_provider.return_value = mock_provider
        yield mock_provider

@pytest.fixture
def mock_chroma():
    with patch("app.agents.jd_agent.get_job_collection") as mock_get_collection:
        mock_collection = MagicMock()
        mock_get_collection.return_value = mock_collection
        yield mock_collection

def test_process_job_description(mock_llm_provider, mock_chroma):
    mock_parsed_data = JobParsedData(
        title="Backend Engineer",
        company="TechCorp",
        location="Remote",
        salary="$120k - $150k",
        required_skills=["Python", "FastAPI", "PostgreSQL"],
        preferred_skills=["Docker", "Kubernetes"],
        responsibilities=["Build and maintain scalable APIs"],
        experience_requirements="5+ years"
    )
    mock_llm_provider.generate_structured_output.return_value = mock_parsed_data
    
    parsed_data, doc_id = process_and_store_job(MOCK_JD_TEXT, provider_name="openai")
    
    assert parsed_data.title == "Backend Engineer"
    assert parsed_data.company == "TechCorp"
    assert "Python" in parsed_data.required_skills
    assert "Docker" in parsed_data.preferred_skills
    
    mock_chroma.add.assert_called_once()
