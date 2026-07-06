from sqlalchemy import Column, Integer, String, Boolean, JSON, ForeignKey
from app.db.session import Base

class UserProfile(Base):
    __tablename__ = "user_profiles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, index=True)
    
    # Core Details
    first_name = Column(String, nullable=True)
    last_name = Column(String, nullable=True)
    email = Column(String, nullable=True)
    phone = Column(String, nullable=True)
    
    # Professional Links
    github_url = Column(String, nullable=True)
    portfolio_url = Column(String, nullable=True)
    linkedin_url = Column(String, nullable=True)
    
    # Qualifications
    experience = Column(JSON, default=[]) # e.g. [{"title": "SE", "company": "X", "years": 2}]
    education = Column(JSON, default=[])
    skills = Column(JSON, default=[])
    
    # Logistics
    expected_salary = Column(String, nullable=True)
    visa_required = Column(Boolean, default=False)
    location = Column(String, nullable=True)
    notice_period = Column(String, nullable=True)
    work_authorization = Column(String, nullable=True)
