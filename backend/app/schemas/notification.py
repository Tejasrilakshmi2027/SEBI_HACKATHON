from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from app.models.notification import NotificationType


class NotificationResponse(BaseModel):
    id: int
    notification_type: NotificationType
    title: str
    message: str
    is_read: bool
    action_url: Optional[str] = None
    created_at: datetime
    
    class Config:
        from_attributes = True
