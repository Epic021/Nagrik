"""
AI Classification Routes

Endpoints for Gemini-powered category classification
before complaint submission.
"""
from typing import Optional
from fastapi import APIRouter, HTTPException, Query, status
from pydantic import BaseModel

from ..services.gemini_ai import (
    classify_complaint_from_image,
    classify_complaint_from_text,
    extract_location_from_text,
    analyze_complaint_severity
)

router = APIRouter(prefix="/classify", tags=["AI Classification"])


class TextClassifyRequest(BaseModel):
    title: str
    description: str


class ImageClassifyRequest(BaseModel):
    image_url: str
    description: Optional[str] = None


@router.post("/from-image")
async def classify_from_image(request: ImageClassifyRequest):
    """
    Classify complaint category from an image using Gemini Vision.
    
    Call this after uploading an image to get AI-suggested category.
    
    Flow:
    1. User uploads image → /files/upload
    2. Call /classify/from-image with the image URL
    3. Get suggested category + urgency
    4. User confirms or changes category
    5. Submit complaint with category_id
    """
    result = await classify_complaint_from_image(
        image_url=request.image_url,
        description=request.description
    )
    
    if result.get("fallback"):
        # Gemini not configured - return helpful error
        return {
            "success": False,
            "error": result.get("error", "AI classification not available"),
            "message": "Please select category manually or configure GEMINI_API_KEY"
        }
    
    # If Gemini extraction is available, attempt to get location too
    location_result = await extract_location_from_text(request.description or "")
    
    return {
        "success": True,
        "category_id": result.get("category_id"),
        "category_name": result.get("category_name"),
        "confidence": result.get("confidence", 0),
        "detected_issues": result.get("detected_issues", []),
        "suggested_urgency": result.get("suggested_urgency", "medium"),
        "ai_description": result.get("ai_description", ""),
        "location": location_result if location_result and location_result.get("has_location") else None
    }


@router.post("/from-text")
async def classify_from_text(request: TextClassifyRequest):
    """
    Classify complaint category from text description using Gemini.
    
    Use when user doesn't have an image.
    """
    result = await classify_complaint_from_text(
        title=request.title,
        description=request.description
    )
    
    if result.get("fallback"):
        return {
            "success": False,
            "error": result.get("error", "AI classification not available"),
            "message": "Please select category manually or configure GEMINI_API_KEY"
        }
    
    # If Gemini extraction is available, attempt to get location too
    location_result = await extract_location_from_text(f"{request.title} {request.description}")
    
    return {
        "success": True,
        "category_id": result.get("category_id"),
        "category_name": result.get("category_name"),
        "confidence": result.get("confidence", 0),
        "suggested_urgency": result.get("suggested_urgency", "medium"),
        "reasoning": result.get("reasoning", ""),
        "location": location_result if location_result and location_result.get("has_location") else None
    }


@router.post("/extract-location")
async def extract_location(text: str = Query(..., description="Text to extract location from")):
    """
    Extract location information from complaint text using Gemini.
    
    Use when user provides text-based location instead of GPS.
    """
    result = await extract_location_from_text(text)
    
    if not result:
        return {
            "success": False,
            "message": "Could not extract location or GEMINI_API_KEY not configured"
        }
    
    return {
        "success": True,
        "has_location": result.get("has_location", False),
        "address": result.get("address", ""),
        "locality": result.get("locality", ""),
        "landmark": result.get("landmark", "")
    }


@router.post("/analyze-severity")
async def analyze_severity(
    title: str = Query(...),
    description: str = Query(...),
    category_id: str = Query(...),
    image_url: Optional[str] = Query(None)
):
    """
    Analyze complaint severity and urgency using Gemini.
    
    Called after classification to determine priority.
    """
    result = await analyze_complaint_severity(
        title=title,
        description=description,
        category_id=category_id,
        image_url=image_url
    )
    
    return {
        "urgency": result.get("urgency", "medium"),
        "severity_score": result.get("severity_score", 0.5),
        "is_emergency": result.get("is_emergency", False),
        "requires_immediate_action": result.get("requires_immediate_action", False),
        "reasoning": result.get("reasoning", "")
    }
