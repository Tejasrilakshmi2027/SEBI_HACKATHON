from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
import time

from app.db.session import get_db
from app.schemas.scan import ScanCreate, ScanResponse, ScanResult
from app.services.scan_service import ScanService
from app.core.deps import get_current_user
from app.models.user import User
from app.utils.file_handler import save_upload_file
from app.ai_models.email_phishing.detector import EmailPhishingDetector
from app.ai_models.url_scanner.scanner import URLScanner
from app.ai_models.pdf_verification.verifier import PDFVerifier
from app.ai_models.image_deepfake.detector import ImageDeepfakeDetector
from app.ai_models.video_deepfake.detector import VideoDeepfakeDetector
from app.ai_models.audio_analysis.analyzer import AudioAnalyzer
from app.ai_models.social_media.scanner import SocialMediaScanner
from app.ai_models.trust_engine.engine import TrustEngine
from app.models.scan import ScanType

router = APIRouter()


@router.post("/upload", response_model=ScanResponse)
async def upload_and_scan(
    file: UploadFile = File(...),
    scan_type: ScanType = ScanType.image,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Upload file and perform security scan."""
    start_time = time.time()
    
    # Save uploaded file
    file_path = await save_upload_file(file)
    file_size = len(await file.read())
    await file.seek(0)
    
    # Create scan record
    scan_in = ScanCreate(scan_type=scan_type)
    scan = await ScanService.create_scan(
        db, 
        user_id=current_user.id,
        scan_in=scan_in,
        file_name=file.filename,
        file_path=file_path,
        file_size=file_size
    )
    
    # Perform analysis based on scan type
    result = None
    
    if scan_type == ScanType.email:
        detector = EmailPhishingDetector()
        result = await detector.analyze(file_path)
    elif scan_type == ScanType.url:
        scanner = URLScanner()
        result = await scanner.scan(file_path)
    elif scan_type == ScanType.pdf:
        verifier = PDFVerifier()
        result = await verifier.verify(file_path)
    elif scan_type == ScanType.image:
        detector = ImageDeepfakeDetector()
        result = await detector.detect(file_path)
    elif scan_type == ScanType.video:
        detector = VideoDeepfakeDetector()
        result = await detector.detect(file_path)
    elif scan_type == ScanType.audio:
        analyzer = AudioAnalyzer()
        result = await analyzer.analyze(file_path)
    elif scan_type == ScanType.social_media:
        scanner = SocialMediaScanner()
        result = await scanner.scan(file_path)
    else:
        # Default generic analysis
        trust_engine = TrustEngine()
        result = await trust_engine.analyze(file_path, scan_type)
    
    # Calculate trust score using Trust Engine
    trust_engine = TrustEngine()
    final_result = await trust_engine.compute_trust_score(result, scan_type)
    
    # Update scan with results
    processing_time = time.time() - start_time
    updated_scan = await ScanService.update_scan_result(db, scan.id, final_result, processing_time)
    
    return updated_scan


@router.post("/scan-url", response_model=ScanResponse)
async def scan_url(
    url: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Scan a URL for security threats."""
    start_time = time.time()
    
    # Create scan record
    scan_in = ScanCreate(scan_type=ScanType.url, url=url)
    scan = await ScanService.create_scan(db, current_user.id, scan_in)
    
    # Perform URL scanning
    scanner = URLScanner()
    result = await scanner.scan_url(url)
    
    # Calculate trust score
    trust_engine = TrustEngine()
    final_result = await trust_engine.compute_trust_score(result, ScanType.url)
    
    # Update scan with results
    processing_time = time.time() - start_time
    updated_scan = await ScanService.update_scan_result(db, scan.id, final_result, processing_time)
    
    return updated_scan


@router.get("/history", response_model=List[dict])
async def get_scan_history(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get user's scan history."""
    scans = await ScanService.get_user_scans(db, current_user.id, skip, limit)
    
    history = []
    for scan in scans:
        import json
        history.append({
            "id": scan.id,
            "scan_type": scan.scan_type,
            "file_name": scan.file_name,
            "url": scan.url,
            "trust_score": scan.trust_score,
            "risk_level": scan.risk_level,
            "created_at": scan.created_at
        })
    
    return history


@router.get("/{scan_id}", response_model=ScanResponse)
async def get_scan(
    scan_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get detailed scan results."""
    scan = await ScanService.get_by_id(db, scan_id)
    
    if not scan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Scan not found"
        )
    
    if scan.user_id != current_user.id and current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this scan"
        )
    
    import json
    return {
        "id": scan.id,
        "user_id": scan.user_id,
        "scan_type": scan.scan_type,
        "file_name": scan.file_name,
        "file_path": scan.file_path,
        "file_size": scan.file_size,
        "url": scan.url,
        "trust_score": scan.trust_score,
        "risk_level": scan.risk_level,
        "confidence": scan.confidence,
        "reasons": json.loads(scan.reasons) if scan.reasons else [],
        "evidence": json.loads(scan.evidence) if scan.evidence else [],
        "recommendations": json.loads(scan.recommendations) if scan.recommendations else [],
        "analysis_result": json.loads(scan.analysis_result) if scan.analysis_result else {},
        "status": scan.status,
        "processing_time": scan.processing_time,
        "created_at": scan.created_at
    }
