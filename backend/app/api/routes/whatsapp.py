"""
WhatsApp Bot API Routes

Endpoints for WhatsApp bot integration with Gemini AI chat.
These endpoints are called by the Baileys WhatsApp client.
"""

from fastapi import APIRouter, HTTPException, status
from typing import List, Optional
from pydantic import BaseModel

from ..models.whatsapp import (
    ChatRequest,
    ChatResponse,
    ClearSessionRequest,
    ClearSessionResponse,
    HealthResponse
)
from ..services.whatsapp_bot import (
    generate_chat_response,
    clear_session,
    get_active_sessions_count
)
from ..core.database import get_db

router = APIRouter(prefix="/whatsapp", tags=["WhatsApp Bot"])


class ComplaintStatus(BaseModel):
    id: str
    title: str
    status: str
    category: str
    created_at: Optional[str] = None


class StatusResponse(BaseModel):
    success: bool
    complaints: List[ComplaintStatus]
    message: Optional[str] = None


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Process a chat message from WhatsApp user.
    
    - **user_id**: WhatsApp phone number (e.g., 919876543210@s.whatsapp.net)
    - **message**: Text message from user
    - **image**: Base64 encoded image (optional)
    """
    if not request.user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="user_id is required"
        )
    
    if not request.message and not request.image:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Either message or image must be provided"
        )
    
    result = await generate_chat_response(
        user_id=request.user_id,
        message=request.message,
        image_base64=request.image
    )
    
    # Always return the response text (even if there was an error)
    return ChatResponse(
        response=result.get('response', 'Sorry, something went wrong.'),
        success=result.get('success', False)
    )


@router.post("/clear", response_model=ClearSessionResponse)
async def clear(request: ClearSessionRequest):
    """Clear conversation session for a WhatsApp user."""
    result = await clear_session(request.user_id)
    
    return ClearSessionResponse(
        success=result['success'],
        message=result['message']
    )


@router.get("/health", response_model=HealthResponse)
async def health():
    """Health check endpoint for WhatsApp bot service."""
    return HealthResponse(
        status="ok",
        active_sessions=get_active_sessions_count()
    )


@router.get("/status/{phone}", response_model=StatusResponse)
async def get_user_complaints(phone: str):
    """
    Get recent complaints for a phone number.
    User can type STATUS in WhatsApp to check their complaints.
    """
    db = get_db()
    
    # Clean phone number
    phone = phone.replace("+", "").replace(" ", "").replace("-", "")
    if phone.startswith("91") and len(phone) > 10:
        phone = phone[2:]
    
    # Find user
    user = await db.users.find_one({"phone": phone})
    if not user:
        return StatusResponse(
            success=True,
            complaints=[],
            message="No complaints found for this number"
        )
    
    # Get recent complaints
    complaints = await db.complaints.find(
        {"created_by.id": str(user["_id"])}
    ).sort("created_at", -1).limit(5).to_list(5)
    
    result = []
    for c in complaints:
        result.append(ComplaintStatus(
            id=str(c["_id"]),
            title=c.get("title", "")[:50],
            status=c.get("status", "pending"),
            category=c.get("category", {}).get("name", "Other"),
            created_at=c["created_at"].isoformat() if c.get("created_at") else None
        ))
    
    return StatusResponse(
        success=True,
        complaints=result,
        message=f"Found {len(result)} complaint(s)"
    )

