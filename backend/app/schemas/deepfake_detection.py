"""
Pydantic schemas for Deepfake Detection
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any


class ManipulationRegion(BaseModel):
    """Manipulation region in image"""
    x: int
    y: int
    width: int
    height: int
    blur_anomaly: float
    edge_anomaly: float
    confidence: float


class DeepfakeDetectionResponse(BaseModel):
    """Response for deepfake detection"""
    is_deepfake: bool
    confidence: float = Field(..., ge=0, le=1, description="Confidence score (0-1)")
    trust_score: int = Field(..., ge=0, le=100, description="Trust score (0-100)")
    risk_level: str = Field(..., description="Risk level: low, medium, high, critical")
    features: Dict[str, float]
    manipulation_regions: List[ManipulationRegion]
    visualization_path: Optional[str] = None
    recommendations: List[str]
    user_id: Optional[int] = None
    scan_type: Optional[str] = None
    file_name: Optional[str] = None


class BatchDeepfakeDetectionResponse(BaseModel):
    """Response for batch deepfake detection"""
    results: List[Dict[str, Any]]
    total: int
    deepfake_count: int
