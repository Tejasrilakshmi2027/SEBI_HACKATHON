from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
from app.models.notification import Notification, NotificationType
from app.schemas.notification import NotificationResponse


class NotificationService:
    @staticmethod
    async def create_notification(db: AsyncSession, user_id: int, 
                                  notification_type: NotificationType,
                                  title: str, message: str, 
                                  action_url: str = None) -> Notification:
        notification = Notification(
            user_id=user_id,
            notification_type=notification_type,
            title=title,
            message=message,
            action_url=action_url
        )
        db.add(notification)
        await db.commit()
        await db.refresh(notification)
        return notification
    
    @staticmethod
    async def get_user_notifications(db: AsyncSession, user_id: int, 
                                     unread_only: bool = False, 
                                     limit: int = 50) -> List[Notification]:
        query = select(Notification).where(Notification.user_id == user_id)
        
        if unread_only:
            query = query.where(Notification.is_read == False)
        
        query = query.order_by(Notification.created_at.desc()).limit(limit)
        
        result = await db.execute(query)
        return result.scalars().all()
    
    @staticmethod
    async def mark_as_read(db: AsyncSession, notification_id: int) -> bool:
        result = await db.execute(
            select(Notification).where(Notification.id == notification_id)
        )
        notification = result.scalar_one_or_none()
        
        if notification:
            notification.is_read = True
            await db.commit()
            return True
        return False
    
    @staticmethod
    async def mark_all_as_read(db: AsyncSession, user_id: int) -> int:
        result = await db.execute(
            select(Notification).where(
                Notification.user_id == user_id,
                Notification.is_read == False
            )
        )
        notifications = result.scalars().all()
        
        count = 0
        for notification in notifications:
            notification.is_read = True
            count += 1
        
        await db.commit()
        return count
