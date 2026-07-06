import logging
from typing import List
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.db.models.user import User
from app.db.models.notification import Notification
from app.api.deps import get_current_active_user
from app.schemas.notification import NotificationCreate, NotificationResponse

logger = logging.getLogger(__name__)
router = APIRouter()

import os

def send_email_mock(email: str, title: str, message: str):
    # Simulates an SMTP outbox by appending to a local file
    os.makedirs("storage", exist_ok=True)
    with open("storage/emails.log", "a") as f:
        f.write(f"--- MOCK EMAIL TO {email} ---\n")
        f.write(f"SUBJECT: {title}\n")
        f.write(f"BODY: {message}\n")
        f.write("-----------------------------\n")
    logger.info(f"Email successfully dispatched to SMTP outbox for {email}")

@router.post("/", response_model=NotificationResponse)
def create_notification(
    request: NotificationCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Creates an in-app notification and dispatches an asynchronous email.
    """
    db_notif = Notification(
        user_id=current_user.id,
        title=request.title,
        message=request.message,
        notification_type=request.notification_type
    )
    db.add(db_notif)
    db.commit()
    db.refresh(db_notif)
    
    if request.notification_type == "EMAIL":
        background_tasks.add_task(send_email_mock, current_user.email, request.title, request.message)
        
    return db_notif

@router.get("/", response_model=List[NotificationResponse])
def get_notifications(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    return db.query(Notification).filter(Notification.user_id == current_user.id).order_by(Notification.created_at.desc()).all()

@router.put("/{notif_id}/read", response_model=NotificationResponse)
def mark_notification_read(
    notif_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    notif = db.query(Notification).filter(Notification.id == notif_id, Notification.user_id == current_user.id).first()
    if not notif:
        raise HTTPException(status_code=404, detail="Notification not found")
        
    notif.is_read = True
    db.commit()
    db.refresh(notif)
    return notif
