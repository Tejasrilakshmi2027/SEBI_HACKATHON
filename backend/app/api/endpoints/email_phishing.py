"""
Email Phishing Detection API Endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict, Any
import logging

from app.db.session import get_db
from app.api.dependencies import get_current_user
from app.models.user import User
from app.services.email_phishing_service import email_phishing_service
from app.schemas.email_phishing import (
    EmailPhishingRequest,
    EmailPhishingResponse,
    BatchEmailPhishingRequest,
    BatchEmailPhishingResponse,
    FeatureImportanceResponse
)

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/detect", response_model=EmailPhishingResponse)
async def detect_phishing(
    request: EmailPhishingRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Detect if an email is phishing
    
    Analyzes email content using trained BERT model and returns:
    - Phishing prediction
    - Confidence score
    - Risk level
    - Trust score
    - Explanations with highlighted regions
    - Actionable recommendations
    - Sender spoofing detection
    - Credential harvesting detection
    - AI-generated pattern detection
    """
    try:
        logger.info(f"Phishing detection request from user {current_user.id}")
        
        # Detect phishing
        result = email_phishing_service.detect_phishing(request.email_content, is_eml=request.is_eml)
        
        # Add metadata
        result["user_id"] = current_user.id
        result["scan_type"] = "email_phishing"
        
        return EmailPhishingResponse(**result)
        
    except Exception as e:
        logger.error(f"Error in phishing detection: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error detecting phishing: {str(e)}"
        )


@router.post("/batch-detect", response_model=BatchEmailPhishingResponse)
async def batch_detect_phishing(
    request: BatchEmailPhishingRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Detect phishing for multiple emails
    
    Analyzes multiple email contents and returns predictions for each.
    """
    try:
        logger.info(f"Batch phishing detection request from user {current_user.id} for {len(request.emails)} emails")
        
        # Detect phishing for all emails
        results = email_phishing_service.batch_detect(request.emails)
        
        # Add metadata
        for result in results:
            result["user_id"] = current_user.id
            result["scan_type"] = "email_phishing"
        
        return BatchEmailPhishingResponse(
            results=results,
            total=len(results),
            phishing_count=sum(1 for r in results if r.get("is_phishing", False))
        )
        
    except Exception as e:
        logger.error(f"Error in batch phishing detection: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error in batch detection: {str(e)}"
        )


@router.post("/feature-importance", response_model=FeatureImportanceResponse)
async def get_feature_importance(
    request: EmailPhishingRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get feature importance for email analysis
    
    Returns detailed feature importance scores for explainability.
    """
    try:
        logger.info(f"Feature importance request from user {current_user.id}")
        
        # Get feature importance
        result = email_phishing_service.get_feature_importance(request.email_content)
        
        return FeatureImportanceResponse(**result)
        
    except Exception as e:
        logger.error(f"Error getting feature importance: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting feature importance: {str(e)}"
        )


@router.get("/health")
async def health_check():
    """Health check endpoint for the phishing detection service"""
    try:
        # Test if service is initialized
        _ = email_phishing_service._detector
        return {"status": "healthy", "service": "email_phishing_detection"}
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}
