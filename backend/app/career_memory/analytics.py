from sqlalchemy.orm import Session
from sqlalchemy import func
from app.db.models.application import Application, ApplicationStatus
from app.db.models.career_memory import MemoryCompany, MemoryEvent, MemoryInterview
from app.db.models.application_package import ApplicationPackage
from app.career_memory.models import AnalyticsReport
import json

class CareerAnalytics:
    @staticmethod
    def generate_report(db: Session, user_id: int) -> AnalyticsReport:
        # Applications stats
        total_apps = db.query(Application).filter(Application.user_id == user_id).count()
        interviews = db.query(Application).filter(Application.user_id == user_id, Application.status == ApplicationStatus.INTERVIEW).count()
        offers = db.query(Application).filter(Application.user_id == user_id, Application.status == ApplicationStatus.OFFER).count()
        
        app_success_rate = (interviews + offers) / total_apps * 100 if total_apps > 0 else 0
        interview_rate = interviews / total_apps * 100 if total_apps > 0 else 0
        offer_rate = offers / total_apps * 100 if total_apps > 0 else 0
        
        # ATS Stats
        ats_scores = db.query(ApplicationPackage.ats_score).filter(ApplicationPackage.user_id == user_id, ApplicationPackage.ats_score.isnot(None)).all()
        avg_ats = sum([s[0] for s in ats_scores]) / len(ats_scores) if ats_scores else 0
        
        # Missing skills (simplified extraction from packages)
        packages = db.query(ApplicationPackage.skill_gap_json).filter(ApplicationPackage.user_id == user_id).all()
        skill_counts = {}
        for p in packages:
            if p[0] and isinstance(p[0], dict) and 'missing_skills' in p[0]:
                for s in p[0]['missing_skills']:
                    skill_counts[s] = skill_counts.get(s, 0) + 1
        
        top_skills = sorted(skill_counts.items(), key=lambda x: x[1], reverse=True)[:5]
        
        # Top Companies
        top_companies = db.query(MemoryCompany.name, MemoryCompany.jobs_applied).filter(MemoryCompany.user_id == user_id).order_by(MemoryCompany.jobs_applied.desc()).limit(5).all()

        return AnalyticsReport(
            application_success_rate=round(app_success_rate, 2),
            interview_rate=round(interview_rate, 2),
            offer_rate=round(offer_rate, 2),
            average_ats_score=round(avg_ats, 2),
            top_performing_resume_id=None, # To be implemented via resume_history
            most_common_missing_skills=[s[0] for s in top_skills],
            most_targeted_companies=[c[0] for c in top_companies],
            most_targeted_roles=["Software Engineer", "Backend Developer"], # Placeholder for aggregation
            monthly_statistics={"Applications": total_apps}
        )
