"""Service to handle document uploads and storage."""
import os
from pathlib import Path
from fastapi import HTTPException, UploadFile


# Base uploads directory
UPLOADS_DIR = Path(__file__).parent.parent.parent / "uploads"
ALLOWED_EXTENSIONS = {".pdf"}


def ensure_upload_dir(subdir: str) -> Path:
    """Ensure upload subdirectory exists."""
    target_dir = UPLOADS_DIR / subdir
    target_dir.mkdir(parents=True, exist_ok=True)
    return target_dir


async def upload_document(file: UploadFile, subdir: str, filename: str) -> str:
    """
    Upload a PDF document and return the file path (relative).
    
    Args:
        file: UploadFile from FastAPI
        subdir: subdirectory (e.g., 'kyc/1', 'loans/personal/1')
        filename: desired filename (e.g., 'pan_card.pdf', 'pay_slip.pdf')
    
    Returns:
        Relative file path suitable for storage in DB
    """
    if not file.filename:
        raise HTTPException(status_code=400, detail="File has no name")
    
    # Validate file extension
    file_ext = Path(file.filename).suffix.lower()
    if file_ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail=f"Only PDF files allowed; got {file_ext}")
    
    # Ensure directory exists
    target_dir = ensure_upload_dir(subdir)
    
    # Save file
    file_path = target_dir / filename
    try:
        contents = await file.read()
        with open(file_path, "wb") as f:
            f.write(contents)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save file: {str(e)}")
    
    # Return relative path for DB storage
    relative_path = str(file_path.relative_to(UPLOADS_DIR.parent))
    return relative_path


def get_document_path(doc_path: str) -> Path:
    """
    Get full file path from stored relative path.
    Useful for serving/downloading files.
    """
    full_path = UPLOADS_DIR.parent / doc_path
    if not full_path.exists():
        raise HTTPException(status_code=404, detail="Document not found")
    return full_path
