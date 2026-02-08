import uuid
from fastapi import APIRouter, HTTPException, UploadFile, File, status, Depends
from google.cloud import storage
from google.oauth2 import service_account

from ..core.config import get_settings
from .auth import get_current_user

router = APIRouter(prefix="/files", tags=["File Upload"])
settings = get_settings()


def get_gcs_client():
    """Get Google Cloud Storage client."""
    if not settings.GCS_SERVICE_ACCOUNT_KEY:
        return None
    
    credentials = service_account.Credentials.from_service_account_file(
        settings.GCS_SERVICE_ACCOUNT_KEY
    )
    return storage.Client(credentials=credentials)


@router.post("/upload")
async def upload_file(
    file: UploadFile = File(...),
    user: dict = Depends(get_current_user)
):
    """
    Upload an image or video file.
    Returns the public URL.
    
    Supported formats: jpg, jpeg, png, gif, webp, mp4, mov
    Max size: 10MB
    """
    # Validate file type
    allowed_extensions = {"jpg", "jpeg", "png", "gif", "webp", "mp4", "mov"}
    ext = file.filename.split(".")[-1].lower() if file.filename else ""
    
    if ext not in allowed_extensions:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File type not allowed. Allowed: {', '.join(allowed_extensions)}"
        )
    
    # Validate file size (10MB max)
    content = await file.read()
    if len(content) > 10 * 1024 * 1024:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File too large. Maximum size is 10MB"
        )
    
    # Generate unique filename
    unique_name = f"complaints/{str(user['_id'])}/{uuid.uuid4()}.{ext}"
    
    # Try to upload to GCS
    client = get_gcs_client()
    
    if client:
        try:
            bucket = client.bucket(settings.GCS_BUCKET_NAME)
            blob = bucket.blob(unique_name)
            blob.upload_from_string(
                content,
                content_type=file.content_type
            )
            blob.make_public()
            
            return {
                "url": blob.public_url,
                "filename": unique_name,
                "size": len(content),
                "content_type": file.content_type
            }
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to upload to cloud storage: {str(e)}"
            )
    else:
        # Mock response for development without GCS
        mock_url = f"https://storage.googleapis.com/{settings.GCS_BUCKET_NAME}/{unique_name}"
        return {
            "url": mock_url,
            "filename": unique_name,
            "size": len(content),
            "content_type": file.content_type,
            "mock": True,
            "message": "GCS not configured - this is a mock URL"
        }
