from pydantic import BaseModel
from typing import List, Dict, Any


class DashboardStats(BaseModel):
    total_scans: int
    high_risk_scans: int
    medium_risk_scans: int
    low_risk_scans: int
    avg_trust_score: float
    threat_trend: List[Dict[str, Any]]
    category_distribution: Dict[str, int]
    recent_scans: List[Dict[str, Any]]
    latest_alerts: List[Dict[str, Any]]


class ThreatHeatmap(BaseModel):
    category: str
    severity: str
    count: int
    timestamp: str
