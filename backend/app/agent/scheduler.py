from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger
from app.core.logger import system_logger
from app.agent.planner import Planner
from app.db.session import SessionLocal

class AgentScheduler:
    """
    Manages automated recurring tasks (Hourly, Daily, Cron).
    """
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(AgentScheduler, cls).__new__(cls)
            cls._instance.scheduler = BackgroundScheduler()
        return cls._instance

    def start(self):
        if not self.scheduler.running:
            self.scheduler.start()
            system_logger.info("Agent Scheduler started.")

    def stop(self):
        if self.scheduler.running:
            self.scheduler.shutdown()
            system_logger.info("Agent Scheduler stopped.")

    def schedule_hourly_planning(self, user_id: int):
        job_id = f"hourly_plan_{user_id}"
        
        def run_planner():
            db = SessionLocal()
            try:
                Planner.plan_next_actions(db, user_id)
            finally:
                db.close()
                
        self.scheduler.add_job(
            run_planner,
            IntervalTrigger(hours=1),
            id=job_id,
            replace_existing=True
        )
        system_logger.info(f"Scheduled hourly planner for user {user_id}")

scheduler_instance = AgentScheduler()
