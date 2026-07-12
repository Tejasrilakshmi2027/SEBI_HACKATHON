from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.db.session import get_db
from app.schemas.notification import NotificationResponse
from app.services.notification_service import NotificationService
from app.core.deps import get_current_user
from app.models.user import User

router = APIRouter()


@router.get("/", response_model=List[NotificationResponse])
async def get_notifications(
    unread_only: bool = False,
    limit: int = 50,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get user notifications."""
    notifications = await NotificationService.get_user_notifications(
        db, current_user.id, unread_only, limit
    )
    return notifications


@router.post("/{notification_id}/read")
async def mark_notification_as_read(
    notification_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Mark notification as read."""
    success = await NotificationService.mark_as_read(db, notification_id)
    return {"success": success}


@router.post("/read-all")
async def mark_all_notifications_as_read(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Mark all notifications as read."""
    count = await NotificationService.mark_all_as_read(db, current_user.id)
    return {"marked_as_read": count}
