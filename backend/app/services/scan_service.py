from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import List, Optional
from datetime import datetime, timedelta
from app.models.scan import Scan, ScanType, RiskLevel
from app.schemas.scan import ScanCreate, ScanResult
import json


class ScanService:
    @staticmethod
    async def create_scan(db: AsyncSession, user_id: int, scan_in: ScanCreate, 
                         file_name: Optional[str] = None, file_path: Optional[str] = None,
                         file_size: Optional[int] = None) -> Scan:
        db_scan = Scan(
            user_id=user_id,
            scan_type=scan_in.scan_type,
            file_name=file_name,
            file_path=file_path,
            file_size=file_size,
            content=scan_in.content,
            url=scan_in.url,
            trust_score=0.0,
            risk_level=RiskLevel.low,
            confidence=0.0,
            status="processing"
        )
        db.add(db_scan)
        await db.commit()
        await db.refresh(db_scan)
        return db_scan
    
    @staticmethod
    async def update_scan_result(db: AsyncSession, scan_id: int, result: ScanResult, 
                                processing_time: float) -> Scan:
        result_obj = await db.execute(select(Scan).where(Scan.id == scan_id))
        scan = result_obj.scalar_one_or_none()
        
        if scan:
            scan.trust_score = result.trust_score
            scan.risk_level = result.risk_level
            scan.confidence = result.confidence
            scan.reasons = json.dumps(result.reasons)
            scan.evidence = json.dumps(result.evidence)
            scan.recommendations = json.dumps(result.recommendations)
            scan.analysis_result = json.dumps(result.analysis_result)
            scan.status = "completed"
            scan.processing_time = processing_time
            await db.commit()
            await db.refresh(scan)
        
        return scan
    
    @staticmethod
    async def get_by_id(db: AsyncSession, scan_id: int) -> Optional[Scan]:
        result = await db.execute(select(Scan).where(Scan.id == scan_id))
        return result.scalar_one_or_none()
    
    @staticmethod
    async def get_user_scans(db: AsyncSession, user_id: int, skip: int = 0, limit: int = 100) -> List[Scan]:
        result = await db.execute(
            select(Scan)
            .where(Scan.user_id == user_id)
            .order_by(Scan.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()
    
    @staticmethod
    async def get_scan_stats(db: AsyncSession, user_id: int) -> dict:
        total_result = await db.execute(
            select(func.count(Scan.id)).where(Scan.user_id == user_id)
        )
        total = total_result.scalar() or 0
        
        high_risk_result = await db.execute(
            select(func.count(Scan.id)).where(
                Scan.user_id == user_id,
                Scan.risk_level == RiskLevel.high
            )
        )
        high_risk = high_risk_result.scalar() or 0
        
        medium_risk_result = await db.execute(
            select(func.count(Scan.id)).where(
                Scan.user_id == user_id,
                Scan.risk_level == RiskLevel.medium
            )
        )
        medium_risk = medium_risk_result.scalar() or 0
        
        low_risk_result = await db.execute(
            select(func.count(Scan.id)).where(
                Scan.user_id == user_id,
                Scan.risk_level == RiskLevel.low
            )
        )
        low_risk = low_risk_result.scalar() or 0
        
        avg_score_result = await db.execute(
            select(func.avg(Scan.trust_score)).where(Scan.user_id == user_id)
        )
        avg_score = avg_score_result.scalar() or 0.0
        
        return {
            "total_scans": total,
            "high_risk_scans": high_risk,
            "medium_risk_scans": medium_risk,
            "low_risk_scans": low_risk,
            "avg_trust_score": round(avg_score, 2)
        }
    
    @staticmethod
    async def get_threat_trend(db: AsyncSession, user_id: int, days: int = 30) -> List[dict]:
        start_date = datetime.utcnow() - timedelta(days=days)
        
        result = await db.execute(
            select(
                func.date(Scan.created_at).label('date'),
                Scan.risk_level,
                func.count(Scan.id).label('count')
            )
            .where(Scan.user_id == user_id, Scan.created_at >= start_date)
            .group_by(func.date(Scan.created_at), Scan.risk_level)
            .order_by(func.date(Scan.created_at))
        )
        
        trend = []
        for row in result:
            trend.append({
                "date": str(row.date),
                "risk_level": row.risk_level,
                "count": row.count
            })
        
        return trend
    
    @staticmethod
    async def get_category_distribution(db: AsyncSession, user_id: int) -> dict:
        result = await db.execute(
            select(Scan.scan_type, func.count(Scan.id))
            .where(Scan.user_id == user_id)
            .group_by(Scan.scan_type)
        )
        
        distribution = {}
        for row in result:
            distribution[row.scan_type] = row.count
        
        return distribution
