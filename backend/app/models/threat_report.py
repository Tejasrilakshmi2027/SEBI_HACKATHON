from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db.session import Base


class ThreatReport(Base):
    __tablename__ = "threat_reports"
    
    id = Column(Integer, primary_key=True, index=True)
    scan_id = Column(Integer, ForeignKey("scans.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    threat_category = Column(String, nullable=False)
    threat_description = Column(Text, nullable=False)
    severity = Column(String, nullable=False)
    
    # Report content
    executive_summary = Column(Text, nullable=True)
    detailed_analysis = Column(Text, nullable=True)
    mitigation_steps = Column(Text, nullable=True)
    
    # Report metadata
    report_format = Column(String, default="pdf", nullable=False)
    file_path = Column(String, nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    scan = relationship("Scan", backref="threat_reports")
    user = relationship("User", backref="threat_reports")
