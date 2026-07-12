from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from app.models.scan import ScanType, RiskLevel


class ScanBase(BaseModel):
    scan_type: ScanType
    url: Optional[str] = None
    content: Optional[str] = None


class ScanCreate(ScanBase):
    pass


class ScanResult(BaseModel):
    trust_score: float = Field(..., ge=0, le=100)
    risk_level: RiskLevel
    confidence: float = Field(..., ge=0, le=1)
    reasons: List[str]
    evidence: List[Dict[str, Any]]
    recommendations: List[str]
    analysis_result: Dict[str, Any]


class ScanResponse(BaseModel):
    id: int
    user_id: int
    scan_type: ScanType
    file_name: Optional[str] = None
    file_path: Optional[str] = None
    file_size: Optional[int] = None
    url: Optional[str] = None
    trust_score: float
    risk_level: RiskLevel
    confidence: float
    reasons: List[str]
    evidence: List[Dict[str, Any]]
    recommendations: List[str]
    analysis_result: Dict[str, Any]
    status: str
    processing_time: Optional[float] = None
    created_at: datetime
    
    class Config):
        from_attributes = True


class ScanHistoryResponse(BaseModel):
    id: int
    scan_type: ScanType
    file_name: Optional[str] = None
    url: Optional[str] = None
    trust_score: float
    risk_level: RiskLevel
    created_at: datetime
    
    class Config:
        from_attributes = True
