import pytest
from unittest.mock import patch, MagicMock
from app.agents.ats_agent import generate_ats_report
from app.schemas.ats import ATSReportData
from app.db.models.resume import Resume

# Golden Resume mock data
GOLDEN_RESUME_DATA = {
    "name": "Aditya M",
    "skills": ["Python", "Machine Learning", "FastAPI"],
    "experience": []
}

@pytest.fixture
def mock_llm_provider():
    with patch("app.core.llm_provider.LLMFactory.get_provider") as mock_get_provider:
        mock_provider = MagicMock()
        mock_get_provider.return_value = mock_provider
        yield mock_provider

def test_generate_ats_report(mock_llm_provider):
    # Mock LLM Response
    mock_report = MagicMock()
    mock_report.overall_score = 85.0
    mock_report.breakdown.formatting_score = 18.0
    mock_report.breakdown.length_score = 10.0
    mock_report.breakdown.section_completeness_score = 15.0
    mock_report.breakdown.action_verbs_score = 17.0
    mock_report.breakdown.quantified_achievements_score = 25.0
    
    # Mock recommendations
    rec = MagicMock()
    rec.category = "Experience"
    rec.priority = "Critical"
    rec.suggestion = "Add experience section"
    mock_report.recommendations = [rec]

    mock_llm_provider.generate_structured_output.return_value = mock_report
    
    mock_resume = Resume(id=1, user_id=1, parsed_data=GOLDEN_RESUME_DATA)
    
    report = generate_ats_report(mock_resume, provider_name="openai")
    
    assert report is not None
    assert report.overall_score == 85.0
    assert report.breakdown.formatting_score == 18.0
    assert len(report.recommendations) == 1
    assert report.recommendations[0].priority == "Critical"
