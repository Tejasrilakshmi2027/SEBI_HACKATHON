"""
Deepfake Detection Service
Integrates with the deepfake detection module for image manipulation detection
"""

import os
import sys
import logging
from typing import Dict, Any, List
import tempfile

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../../ai_models/image_deepfake"))

logger = logging.getLogger(__name__)


class DeepfakeDetectionService:
    """Service for deepfake detection"""
    
    _instance = None
    _analyzer = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if self._analyzer is None:
            self._initialize_analyzer()
    
    def _initialize_analyzer(self):
        """Initialize the deepfake analyzer"""
        try:
            from inference import DeepfakeAnalyzer

            model_path = os.path.join(
                os.path.dirname(__file__),
                "../../../ai_models/image_deepfake/saved_model.pth"
            )
            self._analyzer = DeepfakeAnalyzer(model_path=model_path if os.path.exists(model_path) else None)
            logger.info("Deepfake detection service initialized")
        except Exception as e:
            logger.error(f"Error initializing deepfake analyzer: {e}")
            self._analyzer = None
    
    def detect_deepfake(self, image_file_path: str) -> Dict[str, Any]:
        """
        Detect if an image is a deepfake
        
        Args:
            image_file_path: Path to the image file
            
        Returns:
            Dictionary with detection results including:
            - is_deepfake: Boolean indicating if image is deepfake
            - confidence: Confidence score (0-1)
            - trust_score: Trust score (0-100)
            - risk_level: Risk level (low, medium, high, critical)
            - features: Extracted features
            - manipulation_regions: Detected manipulation regions
            - visualization_path: Path to visualization image
            - recommendations: Actionable recommendations
        """
        try:
            if self._analyzer is None:
                self._initialize_analyzer()

            if self._analyzer is None:
                return {
                    "is_deepfake": False,
                    "confidence": 0.0,
                    "trust_score": 50,
                    "risk_level": "medium",
                    "error": "Deepfake detection service unavailable",
                    "recommendations": ["Install optional AI dependencies to enable deepfake detection"]
                }
            
            result = self._analyzer.predict(image_file_path)
            return result
            
        except Exception as e:
            logger.error(f"Error detecting deepfake: {e}")
            return {
                "is_deepfake": False,
                "confidence": 0.0,
                "trust_score": 50,
                "risk_level": "medium",
                "error": str(e),
                "recommendations": ["Error during detection, please try again"]
            }
    
    def detect_deepfake_bytes(self, image_bytes: bytes, file_extension: str = '.jpg') -> Dict[str, Any]:
        """
        Detect deepfake from image bytes
        
        Args:
            image_bytes: Image file as bytes
            file_extension: File extension for the image
            
        Returns:
            Dictionary with detection results
        """
        try:
            with tempfile.NamedTemporaryFile(delete=False, suffix=file_extension) as tmp_file:
                tmp_file.write(image_bytes)
                tmp_file_path = tmp_file.name
            
            result = self.detect_deepfake(tmp_file_path)
            
            os.unlink(tmp_file_path)
            
            return result
            
        except Exception as e:
            logger.error(f"Error detecting deepfake from bytes: {e}")
            return {
                "is_deepfake": False,
                "confidence": 0.0,
                "trust_score": 50,
                "risk_level": "medium",
                "error": str(e),
                "recommendations": ["Error during detection, please try again"]
            }
    
    def batch_detect_deepfake(self, image_file_paths: List[str]) -> List[Dict[str, Any]]:
        """
        Detect deepfake for multiple images
        
        Args:
            image_file_paths: List of image file paths
            
        Returns:
            List of detection results
        """
        try:
            if self._analyzer is None:
                self._initialize_analyzer()

            if self._analyzer is None:
                return [{"error": "Deepfake detection service unavailable", "trust_score": 50, "risk_level": "medium"} for _ in image_file_paths]
            
            return self._analyzer.batch_predict(image_file_paths)
            
        except Exception as e:
            logger.error(f"Error in batch deepfake detection: {e}")
            return [{"error": str(e), "trust_score": 50, "risk_level": "medium"} for _ in image_file_paths]


deepfake_detection_service = DeepfakeDetectionService()
