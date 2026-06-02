import pytest
from unittest.mock import patch, MagicMock
from app.agents.skill_gap_agent import generate_skill_gap_report
from app.schemas.skill_gap import SkillGapReportData
from app.db.models.resume import Resume
from app.db.models.job import Job

GOLDEN_RESUME_DATA = {
    "name": "Aditya M",
    "skills": ["Python", "FastAPI"]
}

MOCK_JOB_DATA = {
    "required_skills": ["Python", "FastAPI", "Docker", "Kubernetes"],
    "preferred_skills": ["AWS"]
}

@pytest.fixture
def mock_llm_provider():
    with patch("app.core.llm_provider.LLMFactory.get_provider") as mock_get_provider:
        mock_provider = MagicMock()
        mock_get_provider.return_value = mock_provider
        yield mock_provider

def test_generate_skill_gap_report(mock_llm_provider):
    mock_report = MagicMock()
    gap_item = MagicMock()
    gap_item.name = "Docker"
    gap_item.priority = "Critical"
    gap_item.category = "Tool"
    mock_report.missing_items = [gap_item]

    mock_llm_provider.generate_structured_output.return_value = mock_report
    
    mock_resume = Resume(id=1, user_id=1, parsed_data=GOLDEN_RESUME_DATA)
    mock_job = Job(id=1, parsed_data=MOCK_JOB_DATA)
    
    report = generate_skill_gap_report(mock_resume, mock_job, provider_name="openai")
    
    assert report is not None
    assert len(report.missing_items) == 1
    assert report.missing_items[0].name == "Docker"
    assert report.missing_items[0].priority == "Critical"
