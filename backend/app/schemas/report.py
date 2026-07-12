from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class ReportCreate(BaseModel):
    scan_id: int
    report_format: str = "pdf"


class ReportResponse(BaseModel):
    id: int
    scan_id: int
    threat_category: str
    threat_description: str
    severity: str
    executive_summary: Optional[str] = None
    detailed_analysis: Optional[str] = None
    mitigation_steps: Optional[str] = None
    report_format: str
    file_path: Optional[str] = None
    created_at: datetime
    
    class Config:
        from_attributes = True
