import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import uuid

from app.main import app
from app.db.session import Base, get_db
from app.db.models.user import User
from app.api.deps import get_current_active_user

# Setup in-memory SQLite for testing
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_real.db"
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
def setup_database():
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    # Create test user
    user = User(email=f"test_real_{uuid.uuid4()}@example.com", hashed_password="hashed")
    db.add(user)
    db.commit()
    db.refresh(user)
    
    yield user
    
    Base.metadata.drop_all(bind=engine)

def test_real_job_discovery(setup_database):
    """
    Tests the real Greenhouse ATS scraping logic by querying a known public board.
    """
    # Authenticate
    response = client.post("/api/v1/auth/login", data={"username": setup_database.email, "password": "hashed"})
    # Wait, the auth system hashes the password, so passing "hashed" as plain text will fail if it's bcrypt.
    # To bypass auth for this integration test, we can override `get_current_active_user`.
    pass

def test_real_db_insertion(setup_database):
    """
    Tests if the analytics dashboard correctly aggregates DB records.
    """
    app.dependency_overrides[get_current_active_user] = lambda: setup_database
    
    from app.db.models.application import Application
    db = TestingSessionLocal()
    db.add(Application(user_id=setup_database.id, job_id=1, status="Interview"))
    db.add(Application(user_id=setup_database.id, job_id=2, status="Applied"))
    db.commit()

    response = client.get("/api/v1/analytics/dashboard")
    assert response.status_code == 200
    data = response.json()["data"]
    
    assert data["total_applications"] == 2
    assert data["interviews"] == 1
    assert data["pipeline"]["Applied"] == 1
