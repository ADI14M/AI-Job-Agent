import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from unittest.mock import patch, MagicMock

from app.main import app
from app.db.session import Base, get_db
from app.core.security import get_password_hash
from app.db.models.user import User

# Test database
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)

@pytest.fixture(scope="module")
def setup_db():
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    # Create test user
    user = User(
        email="test@example.com",
        hashed_password=get_password_hash("password123"),
        full_name="Test User",
        is_active=True
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    yield db
    db.close()
    Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="module")
def auth_headers(setup_db):
    response = client.post(
        "/api/v1/auth/login",
        data={"username": "test@example.com", "password": "password123"}
    )
    assert response.status_code == 200
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}

def test_auth_login(setup_db):
    response = client.post(
        "/api/v1/auth/login",
        data={"username": "test@example.com", "password": "password123"}
    )
    assert response.status_code == 200
    assert "access_token" in response.json()

def test_get_me(auth_headers):
    response = client.get("/api/v1/auth/me", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["email"] == "test@example.com"

# The following tests would normally mock LLM calls and file processing.
# In an audit script without API keys, we mock the `process_and_store_resume` etc.

@patch("app.api.routes.job_discovery.JobDiscoveryAgent.run_discovery")
def test_job_discovery(mock_run, auth_headers):
    mock_run.return_value = []
    response = client.post(
        "/api/v1/job_discovery/run",
        json={"query": "Engineer", "location": "Remote", "platforms": ["linkedin"], "limit": 1},
        headers=auth_headers
    )
    assert response.status_code == 200
    assert response.json()["status"] == "Success"

def test_application_tracker(auth_headers):
    # Creating a mock application
    response = client.post(
        "/api/v1/applications/",
        json={"job_id": 999, "notes": "Test application"},
        headers=auth_headers
    )
    assert response.status_code == 200
    app_id = response.json()["id"]
    
    # Update status to Applied
    update_res = client.put(
        f"/api/v1/applications/{app_id}",
        json={"status": "Applied"},
        headers=auth_headers
    )
    assert update_res.status_code == 200
    assert update_res.json()["status"] == "Applied"
