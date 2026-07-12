"""
Email Phishing Detection Service
Integrates with the trained BERT model for phishing detection
"""

import os
import sys
import logging
from typing import Dict, Any, Optional

# Add AI models directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../../ai_models/email_phishing"))

logger = logging.getLogger(__name__)


class EmailPhishingService:
    """Service for email phishing detection"""
    
    _instance = None
    _detector = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if self._detector is None:
            self._initialize_detector()
    
    def _initialize_detector(self):
        """Initialize the phishing detector"""
        try:
            from inference import EmailPhishingDetector as DetectorClass

            model_path = os.path.join(
                os.path.dirname(__file__), 
                "../../../ai_models/email_phishing/saved_model"
            )
            
            # Check if model exists
            if os.path.exists(model_path):
                logger.info(f"Loading email phishing model from {model_path}")
                self._detector = DetectorClass(model_path=model_path)
            else:
                logger.warning(f"Model not found at {model_path}, using base model")
                self._detector = DetectorClass(model_path="bert-base-uncased")
                
        except Exception as e:
            logger.error(f"Error initializing email phishing detector: {e}")
            self._detector = None
    
    def detect_phishing(self, email_content: str, is_eml: bool = False) -> Dict[str, Any]:
        """
        Detect if an email is phishing
        
        Args:
            email_content: The email content to analyze (text or .eml file path)
            is_eml: Whether the content is an .eml file path
            
        Returns:
            Dictionary with detection results including:
            - is_phishing: Boolean indicating if email is phishing
            - confidence: Confidence score (0-1)
            - risk_level: Risk level (low, medium, high, critical)
            - trust_score: Trust score (0-100)
            - explanations: List of explanations
            - highlighted_regions: Text regions to highlight
            - recommendations: Actionable recommendations
            - spoofing_detection: Sender spoofing detection results
            - credential_detection: Credential harvesting detection results
            - ai_detection: AI-generated pattern detection results
        """
        try:
            if self._detector is None:
                self._initialize_detector()

            if self._detector is None:
                return {
                    "is_phishing": False,
                    "confidence": 0.0,
                    "risk_level": "low",
                    "trust_score": 50,
                    "explanations": [{"type": "error", "message": "Detection service unavailable", "severity": "error"}],
                    "highlighted_regions": [],
                    "recommendations": ["Install optional AI dependencies to enable phishing detection"]
                }
            
            result = self._detector.predict(email_content, return_explanations=True, is_eml=is_eml)
            
            # Add recommendations
            result["recommendations"] = self._detector.get_recommendations(result)
            
            return result
            
        except Exception as e:
            logger.error(f"Error detecting phishing: {e}")
            # Return default result on error
            return {
                "is_phishing": False,
                "confidence": 0.0,
                "risk_level": "low",
                "trust_score": 50,
                "explanations": [{"type": "error", "message": "Detection service unavailable", "severity": "error"}],
                "highlighted_regions": [],
                "recommendations": ["Try again later or contact support"]
            }
    
    def batch_detect(self, emails: list) -> list:
        """
        Detect phishing for multiple emails
        
        Args:
            emails: List of email contents
            
        Returns:
            List of detection results
        """
        try:
            if self._detector is None:
                self._initialize_detector()

            if self._detector is None:
                return [{"error": "Detection service unavailable", "is_phishing": False, "confidence": 0.0, "risk_level": "low"} for _ in emails]
            
            return self._detector.batch_predict(emails)
            
        except Exception as e:
            logger.error(f"Error in batch detection: {e}")
            return [{"error": str(e)} for _ in emails]
    
    def get_feature_importance(self, email_content: str) -> Dict[str, Any]:
        """
        Get feature importance for an email
        
        Args:
            email_content: The email content to analyze
            
        Returns:
            Dictionary with feature importance scores
        """
        try:
            if self._detector is None:
                self._initialize_detector()

            if self._detector is None:
                return {"error": "Detection service unavailable"}
            
            features = self._detector.extract_linguistic_features(
                self._detector.preprocess_email(email_content)
            )
            
            importance = self._detector.get_feature_importance(
                self._detector.preprocess_email(email_content),
                features
            )
            
            return {
                "features": features,
                "importance": importance
            }
            
        except Exception as e:
            logger.error(f"Error getting feature importance: {e}")
            return {"error": str(e)}


# Singleton instance
email_phishing_service = EmailPhishingService()
