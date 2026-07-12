"""
PDF Verification API Endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict, Any
import logging
import tempfile
import os

from app.db.session import get_db
from app.api.dependencies import get_current_user
from app.models.user import User
from app.services.pdf_verification_service import pdf_verification_service
from app.schemas.pdf_verification import PDFVerificationResponse

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/verify", response_model=PDFVerificationResponse)
async def verify_pdf(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Verify a PDF document for forgery
    
    Analyzes PDF using OCR, logo detection, metadata verification, and forgery detection.
    Returns trust score, risk level, and detailed analysis.
    """
    try:
        logger.info(f"PDF verification request from user {current_user.id}")
        
        if not file.filename.endswith('.pdf'):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST_REQUEST,
                detail="Only PDF files are supported"
            )
        
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
            content = await file.read()
            tmp_file.write(content)
            tmp_file_path = tmp_file.name
        
        try:
            result = pdf_verification_service.verify_pdf(tmp_file_path)
            result["user_id"] = current_user.id
            result["scan_type"] = "pdf_verification"
            result["file_name"] = file.filename
            
            return PDFVerificationResponse(**result)
            
        finally:
            os.unlink(tmp_file_path)
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in PDF verification: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error verifying PDF: {str(e)}"
        )


@router.get("/health")
async def health_check():
    """Health check endpoint for the PDF verification service"""
    try:
        _ = pdf_verification_service._verifier
        return {"status": "healthy", "service": "pdf_verification"}
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}
