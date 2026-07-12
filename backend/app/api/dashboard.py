from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.schemas.dashboard import DashboardStats
from app.services.scan_service import ScanService
from app.services.notification_service import NotificationService
from app.core.deps import get_current_user
from app.models.user import User

router = APIRouter()


@router.get("/stats", response_model=DashboardStats)
async def get_dashboard_stats(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get dashboard statistics for current user."""
    # Get scan statistics
    stats = await ScanService.get_scan_stats(db, current_user.id)
    
    # Get threat trend
    threat_trend = await ScanService.get_threat_trend(db, current_user.id, days=30)
    
    # Get category distribution
    category_distribution = await ScanService.get_category_distribution(db, current_user.id)
    
    # Get recent scans
    recent_scans = await ScanService.get_user_scans(db, current_user.id, skip=0, limit=10)
    recent_scans_data = []
    for scan in recent_scans:
        recent_scans_data.append({
            "id": scan.id,
            "scan_type": scan.scan_type,
            "file_name": scan.file_name,
            "trust_score": scan.trust_score,
            "risk_level": scan.risk_level,
            "created_at": scan.created_at.isoformat()
        })
    
    # Get latest alerts (notifications)
    notifications = await NotificationService.get_user_notifications(db, current_user.id, limit=5)
    latest_alerts = []
    for notif in notifications:
        latest_alerts.append({
            "id": notif.id,
            "type": notif.notification_type,
            "title": notif.title,
            "message": notif.message,
            "created_at": notif.created_at.isoformat()
        })
    
    return DashboardStats(
        total_scans=stats["total_scans"],
        high_risk_scans=stats["high_risk_scans"],
        medium_risk_scans=stats["medium_risk_scans"],
        low_risk_scans=stats["low_risk_scans"],
        avg_trust_score=stats["avg_trust_score"],
        threat_trend=threat_trend,
        category_distribution=category_distribution,
        recent_scans=recent_scans_data,
        latest_alerts=latest_alerts
    )
