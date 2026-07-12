"""
Pydantic schemas for PDF Verification
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any


class LogoPosition(BaseModel):
    """Logo position in PDF"""
    logo: str
    page: int
    position: List[int]
    confidence: float


class SignaturePosition(BaseModel):
    """Signature position in PDF"""
    signature: str
    page: int
    position: List[int]
    confidence: float


class ForgeryIndicator(BaseModel):
    """Forgery indicator"""
    type: str
    message: Optional[str] = None
    keyword: Optional[str] = None
    context: Optional[str] = None


class PDFVerificationResponse(BaseModel):
    """Response for PDF verification"""
    is_forged: bool
    confidence: float = Field(..., ge=0, le=1, description="Confidence score (0-1)")
    trust_score: int = Field(..., ge=0, le=100, description="Trust score (0-100)")
    risk_level: str = Field(..., description="Risk level: low, medium, high, critical")
    metadata: Dict[str, Any]
    metadata_verification: Dict[str, Any]
    extracted_text: List[Dict[str, Any]]
    logo_detection: Dict[str, Any]
    signature_detection: Dict[str, Any]
    forgery_indicators: Dict[str, Any]
    recommendations: List[str]
    user_id: Optional[int] = None
    scan_type: Optional[str] = None
    file_name: Optional[str] = None
