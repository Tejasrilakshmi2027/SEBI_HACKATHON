"""
Pydantic schemas for Email Phishing Detection
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any


class HighlightedRegion(BaseModel):
    """Highlighted text region for explainability"""
    text: str
    start: int
    end: int
    reason: str
    severity: str


class Explanation(BaseModel):
    """Explanation for phishing detection"""
    type: str
    message: str
    severity: str


class EmailPhishingRequest(BaseModel):
    """Request for email phishing detection"""
    email_content: str = Field(..., description="The email content to analyze or path to .eml file")
    is_eml: bool = Field(default=False, description="Whether the content is an .eml file path")


class EmailPhishingResponse(BaseModel):
    """Response for email phishing detection"""
    is_phishing: bool
    confidence: float = Field(..., ge=0, le=1, description="Confidence score (0-1)")
    risk_level: str = Field(..., description="Risk level: low, medium, high, critical")
    trust_score: int = Field(..., ge=0, le=100, description="Trust score (0-100)")
    probabilities: Dict[str, float]
    explanations: List[Explanation]
    highlighted_regions: List[HighlightedRegion]
    linguistic_features: Optional[Dict[str, Any]] = None
    recommendations: List[str]
    user_id: Optional[int] = None
    scan_type: Optional[str] = None
    spoofing_detection: Optional[Dict[str, Any]] = None
    credential_detection: Optional[Dict[str, Any]] = None
    ai_detection: Optional[Dict[str, Any]] = None


class BatchEmailPhishingRequest(BaseModel):
    """Request for batch email phishing detection"""
    emails: List[str] = Field(..., description="List of email contents to analyze")


class BatchEmailPhishingResponse(BaseModel):
    """Response for batch email phishing detection"""
    results: List[Dict[str, Any]]
    total: int
    phishing_count: int


class FeatureImportanceResponse(BaseModel):
    """Response for feature importance"""
    features: Dict[str, Any]
    importance: Dict[str, float]
