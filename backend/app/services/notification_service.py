import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from app.core.logger import system_logger
from app.db.models.notification import Notification
from sqlalchemy.orm import Session
import json

class NotificationService:
    @staticmethod
    def send_email(to_address: str, subject: str, body: str):
        smtp_host = os.getenv("SMTP_HOST")
        smtp_port = os.getenv("SMTP_PORT")
        smtp_user = os.getenv("SMTP_USER")
        smtp_pass = os.getenv("SMTP_PASS")
        
        if not all([smtp_host, smtp_port, smtp_user, smtp_pass]):
            system_logger.warning(f"[Mock Email] Missing SMTP config. Would have sent: {subject} to {to_address}")
            return False
            
        try:
            msg = MIMEMultipart()
            msg['From'] = smtp_user
            msg['To'] = to_address
            msg['Subject'] = subject
            msg.attach(MIMEText(body, 'html'))
            
            server = smtplib.SMTP(smtp_host, int(smtp_port))
            server.starttls()
            server.login(smtp_user, smtp_pass)
            server.send_message(msg)
            server.quit()
            system_logger.info(f"Email sent successfully to {to_address}")
            return True
        except Exception as e:
            system_logger.error(f"Failed to send email: {e}")
            return False

    @staticmethod
    def send_toast(db: Session, user_id: int, title: str, message: str, type: str = "info"):
        """
        Saves a notification to the database. The frontend can long-poll or use WebSocket to fetch this.
        """
        try:
            db_notif = Notification(
                user_id=user_id,
                title=title,
                message=message,
                type=type,
                is_read=False
            )
            db.add(db_notif)
            db.commit()
            system_logger.info(f"Toast notification created for user {user_id}: {title}")
        except Exception as e:
            system_logger.error(f"Failed to create toast notification: {e}")

notification_service = NotificationService()
