import pytest
from unittest.mock import patch, MagicMock
from app.services.resume_service import process_and_store_resume
from app.schemas.resume import ResumeParsedData

# Mock Texts simulating different layouts
MULTI_PAGE_TEXT = """
Page 1
John Doe
johndoe@email.com | 555-1234
Experience:
- Software Engineer at TechCorp (2020-Present)
  Built scalable microservices using Python and FastAPI.

Page 2
Education:
- BS Computer Science, State University, 2016-2020
Skills:
- Python, Docker, Kubernetes, AWS
"""

COLUMN_LAYOUT_TEXT = """
Jane Smith                  Skills: Python, React, SQL
jane@email.com              Education: MS CS, MIT
Experience:
Data Scientist at DataCorp
- Analyzed large datasets.
"""

TABLE_LAYOUT_TEXT = """
Name | Email | Phone
Alice | alice@email.com | 555-0000
Experience | Company | Dates
Backend Dev | StartupInc | 2021-2023
"""

@pytest.fixture
def mock_llm_provider():
    with patch("app.core.llm_provider.LLMFactory.get_provider") as mock_get_provider:
        mock_provider = MagicMock()
        mock_get_provider.return_value = mock_provider
        yield mock_provider

@pytest.fixture
def mock_extract_text():
    with patch("app.services.resume_service.extract_text") as mock_extract:
        yield mock_extract

@pytest.fixture
def mock_chroma():
    with patch("app.services.resume_service.get_resume_collection") as mock_get_collection:
        mock_collection = MagicMock()
        mock_get_collection.return_value = mock_collection
        yield mock_collection


def test_process_multi_page_resume(mock_extract_text, mock_llm_provider, mock_chroma):
    mock_extract_text.return_value = MULTI_PAGE_TEXT
    mock_parsed_data = ResumeParsedData(
        name="John Doe",
        email="johndoe@email.com",
        skills=["Python", "Docker", "Kubernetes", "AWS"]
    )
    mock_llm_provider.generate_structured_output.return_value = mock_parsed_data
    
    raw_text, parsed_data, doc_id = process_and_store_resume("dummy.pdf", user_id=1)
    
    assert raw_text == MULTI_PAGE_TEXT
    assert parsed_data.name == "John Doe"
    assert "Python" in parsed_data.skills
    mock_chroma.add.assert_called_once()

def test_process_column_layout_resume(mock_extract_text, mock_llm_provider, mock_chroma):
    mock_extract_text.return_value = COLUMN_LAYOUT_TEXT
    mock_parsed_data = ResumeParsedData(
        name="Jane Smith",
        email="jane@email.com",
        skills=["Python", "React", "SQL"]
    )
    mock_llm_provider.generate_structured_output.return_value = mock_parsed_data
    
    raw_text, parsed_data, doc_id = process_and_store_resume("dummy.pdf", user_id=1)
    
    assert raw_text == COLUMN_LAYOUT_TEXT
    assert parsed_data.name == "Jane Smith"
    mock_chroma.add.assert_called_once()

def test_process_table_layout_resume(mock_extract_text, mock_llm_provider, mock_chroma):
    mock_extract_text.return_value = TABLE_LAYOUT_TEXT
    mock_parsed_data = ResumeParsedData(
        name="Alice",
        email="alice@email.com",
        skills=[]
    )
    mock_llm_provider.generate_structured_output.return_value = mock_parsed_data
    
    raw_text, parsed_data, doc_id = process_and_store_resume("dummy.pdf", user_id=1)
    
    assert raw_text == TABLE_LAYOUT_TEXT
    assert parsed_data.name == "Alice"
    mock_chroma.add.assert_called_once()
