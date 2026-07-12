"""
PDF Verification Service
Integrates with the PDF verification engine for document forgery detection
"""

import os
import sys
import logging
from typing import Dict, Any
import tempfile

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../../ai_models/pdf_verification"))

logger = logging.getLogger(__name__)


class PDFVerificationService:
    """Service for PDF verification"""
    
    _instance = None
    _verifier = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if self._verifier is None:
            self._initialize_verifier()
    
    def _initialize_verifier(self):
        """Initialize the PDF verifier"""
        try:
            from inference import PDFVerifier

            self._verifier = PDFVerifier()
            logger.info("PDF verification service initialized")
        except Exception as e:
            logger.error(f"Error initializing PDF verifier: {e}")
            self._verifier = None
    
    def verify_pdf(self, pdf_file_path: str) -> Dict[str, Any]:
        """
        Verify a PDF document for forgery
        
        Args:
            pdf_file_path: Path to the PDF file
            
        Returns:
            Dictionary with verification results including:
            - is_forged: Boolean indicating if document is forged
            - confidence: Confidence score (0-1)
            - trust_score: Trust score (0-100)
            - risk_level: Risk level (low, medium, high, critical)
            - metadata: PDF metadata
            - metadata_verification: Metadata verification results
            - extracted_text: OCR extracted text
            - logo_detection: Logo detection results
            - signature_detection: Signature detection results
            - forgery_indicators: Forgery indicators
            - recommendations: Actionable recommendations
        """
        try:
            if self._verifier is None:
                self._initialize_verifier()

            if self._verifier is None:
                return {
                    "is_forged": False,
                    "confidence": 0.0,
                    "trust_score": 50,
                    "risk_level": "medium",
                    "error": "PDF verification service unavailable",
                    "recommendations": ["Install optional AI dependencies to enable PDF verification"]
                }
            
            result = self._verifier.verify_pdf(pdf_file_path)
            return result
            
        except Exception as e:
            logger.error(f"Error verifying PDF: {e}")
            return {
                "is_forged": False,
                "confidence": 0.0,
                "trust_score": 50,
                "risk_level": "medium",
                "error": str(e),
                "recommendations": ["Error during verification, please try again"]
            }
    
    def verify_pdf_bytes(self, pdf_bytes: bytes) -> Dict[str, Any]:
        """
        Verify PDF from bytes
        
        Args:
            pdf_bytes: PDF file as bytes
            
        Returns:
            Dictionary with verification results
        """
        try:
            with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
                tmp_file.write(pdf_bytes)
                tmp_file_path = tmp_file.name
            
            result = self.verify_pdf(tmp_file_path)
            
            os.unlink(tmp_file_path)
            
            return result
            
        except Exception as e:
            logger.error(f"Error verifying PDF from bytes: {e}")
            return {
                "is_forged": False,
                "confidence": 0.0,
                "trust_score": 50,
                "risk_level": "medium",
                "error": str(e),
                "recommendations": ["Error during verification, please try again"]
            }


pdf_verification_service = PDFVerificationService()
