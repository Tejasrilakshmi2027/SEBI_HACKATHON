import os
import aiofiles
from fastapi import UploadFile, HTTPException
from pathlib import Path
from app.core.config import settings
import uuid


async def save_upload_file(upload_file: UploadFile, subfolder: str = "") -> str:
    """Save uploaded file to disk and return the file path."""
    
    # Validate file extension
    file_extension = Path(upload_file.filename).suffix.lower()
    if file_extension not in settings.ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"File type {file_extension} is not allowed"
        )
    
    # Create upload directory if it doesn't exist
    upload_dir = Path(settings.UPLOAD_DIR) / subfolder
    upload_dir.mkdir(parents=True, exist_ok=True)
    
    # Generate unique filename
    unique_filename = f"{uuid.uuid4()}{file_extension}"
    file_path = upload_dir / unique_filename
    
    # Save file
    async with aiofiles.open(file_path, 'wb') as f:
        content = await upload_file.read()
        await f.write(content)
    
    return str(file_path)


async def delete_file(file_path: str) -> bool:
    """Delete a file from disk."""
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
            return True
        return False
    except Exception:
        return False


def get_file_size(file_path: str) -> int:
    """Get file size in bytes."""
    try:
        return os.path.getsize(file_path)
    except Exception:
        return 0
