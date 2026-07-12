"""
Deepfake Detection API Endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict, Any, List
import logging
import tempfile
import os

from app.db.session import get_db
from app.api.dependencies import get_current_user
from app.models.user import User
from app.services.deepfake_detection_service import deepfake_detection_service
from app.schemas.deepfake_detection import DeepfakeDetectionResponse, BatchDeepfakeDetectionResponse

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/detect", response_model=DeepfakeDetectionResponse)
async def detect_deepfake(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Detect if an image is a deepfake
    
    Analyzes image using pretrained neural network and returns:
    - Deepfake prediction
    - Confidence score
    - Trust score
    - Risk level
    - Manipulation regions with visualization
    - Actionable recommendations
    """
    try:
        logger.info(f"Deepfake detection request from user {current_user.id}")
        
        allowed_extensions = {'.jpg', '.jpeg', '.png', '.bmp', '.tiff'}
        file_ext = os.path.splitext(file.filename)[1].lower()
        
        if file_ext not in allowed_extensions:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST_REQUEST,
                detail=f"Unsupported file type. Allowed: {', '.join(allowed_extensions)}"
            )
        
        with tempfile.NamedTemporaryFile(delete=False, suffix=file_ext) as tmp_file:
            content = await file.read()
            tmp_file.write(content)
            tmp_file_path = tmp_file.name
        
        try:
            result = deepfake_detection_service.detect_deepfake(tmp_file_path)
            result["user_id"] = current_user.id
            result["scan_type"] = "deepfake_detection"
            result["file_name"] = file.filename
            
            return DeepfakeDetectionResponse(**result)
            
        finally:
            os.unlink(tmp_file_path)
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in deepfake detection: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error detecting deepfake: {str(e)}"
        )


@router.post("/batch-detect", response_model=BatchDeepfakeDetectionResponse)
async def batch_detect_deepfake(
    files: List[UploadFile] = File(...),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Detect deepfake for multiple images
    
    Analyzes multiple images and returns predictions for each.
    """
    try:
        logger.info(f"Batch deepfake detection request from user {current_user.id} for {len(files)} images")
        
        allowed_extensions = {'.jpg', '.jpeg', '.png', '.bmp', '.tiff'}
        image_paths = []
        
        for file in files:
            file_ext = os.path.splitext(file.filename)[1].lower()
            if file_ext not in allowed_extensions:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST_REQUEST,
                    detail=f"Unsupported file type: {file.filename}"
                )
            
            with tempfile.NamedTemporaryFile(delete=False, suffix=file_ext) as tmp_file:
                content = await file.read()
                tmp_file.write(content)
                image_paths.append(tmp_file.name)
        
        try:
            results = deepfake_detection_service.batch_detect_deepfake(image_paths)
            
            for i, result in enumerate(results):
                result["user_id"] = current_user.id
                result["scan_type"] = "deepfake_detection"
                result["file_name"] = files[i].filename
            
            return BatchDeepfakeDetectionResponse(
                results=results,
                total=len(results),
                deepfake_count=sum(1 for r in results if r.get("is_deepfake", False))
            )
            
        finally:
            for path in image_paths:
                os.unlink(path)
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in batch deepfake detection: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error in batch detection: {str(e)}"
        )


@router.get("/health")
async def health_check():
    """Health check endpoint for the deepfake detection service"""
    try:
        _ = deepfake_detection_service._analyzer
        return {"status": "healthy", "service": "deepfake_detection"}
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}
