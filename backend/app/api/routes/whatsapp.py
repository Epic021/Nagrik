"""
WhatsApp Bot API Routes

Endpoints for WhatsApp bot integration with Gemini AI chat.
These endpoints are called by the Baileys WhatsApp client.
"""

from fastapi import APIRouter, HTTPException, status

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

router = APIRouter(prefix="/whatsapp", tags=["WhatsApp Bot"])


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Process a chat message from WhatsApp user.
    
    Accepts text messages and/or images. Uses Gemini AI to generate
    contextual responses based on conversation history.
    
    - **user_id**: WhatsApp phone number or unique identifier
    - **message**: Text message from user (optional if image provided)
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
    
    if not result.get('success'):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=result.get('error', 'Unknown error')
        )
    
    return ChatResponse(
        response=result['response'],
        success=True
    )


@router.post("/clear", response_model=ClearSessionResponse)
async def clear(request: ClearSessionRequest):
    """
    Clear conversation session for a WhatsApp user.
    
    This resets the conversation history, useful when user
    wants to start a fresh complaint or conversation.
    
    - **user_id**: WhatsApp phone number or unique identifier
    """
    result = await clear_session(request.user_id)
    
    return ClearSessionResponse(
        success=result['success'],
        message=result['message']
    )


@router.get("/health", response_model=HealthResponse)
async def health():
    """
    Health check endpoint for WhatsApp bot service.
    
    Returns service status and number of active chat sessions.
    """
    return HealthResponse(
        status="ok",
        active_sessions=get_active_sessions_count()
    )
