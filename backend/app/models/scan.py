from sqlalchemy import Column, Integer, String, Text, Float, DateTime, Enum as SQLEnum, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db.session import Base
import enum


class ScanType(str, enum.Enum):
    email = "email"
    url = "url"
    pdf = "pdf"
    image = "image"
    video = "video"
    audio = "audio"
    social_media = "social_media"
    text = "text"


class RiskLevel(str, enum.Enum):
    low = "low"
    medium = "medium"
    high = "high"
    critical = "critical"


class Scan(Base):
    __tablename__ = "scans"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    scan_type = Column(SQLEnum(ScanType), nullable=False)
    file_name = Column(String, nullable=True)
    file_path = Column(String, nullable=True)
    file_size = Column(Integer, nullable=True)
    content = Column(Text, nullable=True)
    url = Column(String, nullable=True)
    
    # Results
    trust_score = Column(Float, nullable=False)  # 0-100
    risk_level = Column(SQLEnum(RiskLevel), nullable=False)
    confidence = Column(Float, nullable=False)  # 0-1
    
    # Detailed analysis
    analysis_result = Column(Text, nullable=True)  # JSON string
    reasons = Column(Text, nullable=True)  # JSON array
    evidence = Column(Text, nullable=True)  # JSON array
    recommendations = Column(Text, nullable=True)  # JSON array
    
    # Metadata
    status = Column(String, default="completed", nullable=False)
    error_message = Column(Text, nullable=True)
    processing_time = Column(Float, nullable=True)  # in seconds
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User", backref="scans")
