from sqlalchemy.orm import Session
from app.db.models.notification import Notification
from app.core.logger import system_logger

class NotificationService:
    @staticmethod
    def notify(db: Session, user_id: int, message: str, notification_type: str = "INFO"):
        """
        Persists a notification to the database for the frontend to consume.
        """
        # Assuming app.db.models.notification has fields matching this roughly
        notif = Notification(
            user_id=user_id,
            message=message,
            type=notification_type,
            is_read=False
        )
        db.add(notif)
        db.commit()
        system_logger.info(f"Notification sent to user {user_id}: {message}")
        return notif
