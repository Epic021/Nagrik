"""
Gemini AI Integration for NAGRIK

Uses Google's Gemini API for:
1. Category classification from images/text
2. Urgency estimation
3. Location extraction from text
"""
import base64
import httpx
import json
from typing import Optional, List, Dict, Any

from ..core.config import get_settings
from ..models.departments import COMPLAINT_CATEGORIES

settings = get_settings()

# Category IDs for Gemini to choose from
CATEGORY_OPTIONS = [cat.id for cat in COMPLAINT_CATEGORIES]
CATEGORY_NAMES = {cat.id: cat.name for cat in COMPLAINT_CATEGORIES}

# Gemini model - use gemini-2.0-flash (latest)
GEMINI_MODEL = "gemini-2.0-flash"


def get_gemini_client():
    """Get Gemini client with API key."""
    if not settings.GEMINI_API_KEY:
        return None
    
    from google import genai
    client = genai.Client(api_key=settings.GEMINI_API_KEY)
    return client


async def classify_complaint_from_image(
    image_url: str,
    description: Optional[str] = None
) -> Dict[str, Any]:
    """
    Use Gemini Vision to classify complaint category from image.
    
    Returns:
        {
            "category_id": "potholes",
            "category_name": "Potholes & Road Damage",
            "confidence": 0.92,
            "detected_issues": ["pothole", "road damage"],
            "suggested_urgency": "high",
            "ai_description": "Large pothole approximately 2 feet wide..."
        }
    """
    client = get_gemini_client()
    if not client:
        return {
            "success": False,
            "category_id": None,
            "error": "GEMINI_API_KEY not configured",
            "message": "Please select category manually"
        }
    
    try:
        from google.genai import types
        
        # Download image
        async with httpx.AsyncClient() as http_client:
            response = await http_client.get(image_url)
            image_bytes = response.content
        
        # Prepare image for Gemini
        image_part = types.Part.from_bytes(
            data=image_bytes,
            mime_type="image/jpeg"
        )
        
        # Build prompt
        categories_list = "\n".join([f"- {cid}: {CATEGORY_NAMES[cid]}" for cid in CATEGORY_OPTIONS])
        
        prompt = f"""Analyze this civic complaint image and classify it.

Available categories:
{categories_list}

{f"User description: {description}" if description else ""}

Respond in this exact JSON format:
{{
    "category_id": "<category_id from list>",
    "confidence": <0.0 to 1.0>,
    "detected_issues": ["issue1", "issue2"],
    "suggested_urgency": "<low|medium|high|critical>",
    "ai_description": "<brief description of what you see>"
}}

Only respond with valid JSON, no other text."""

        response = client.models.generate_content(
            model=GEMINI_MODEL,
            contents=[prompt, image_part]
        )
        
        # Parse response
        text = response.text.strip()
        # Remove markdown code blocks if present
        if text.startswith("```"):
            text = text.split("\n", 1)[1].rsplit("```", 1)[0]
        
        result = json.loads(text)
        result["success"] = True
        result["category_name"] = CATEGORY_NAMES.get(result.get("category_id"), "Unknown")
        return result
        
    except Exception as e:
        return {
            "success": False,
            "category_id": None,
            "error": str(e),
            "message": "Please select category manually or configure GEMINI_API_KEY"
        }


async def classify_complaint_from_text(
    title: str,
    description: str
) -> Dict[str, Any]:
    """
    Use Gemini to classify complaint category from text description.
    
    Returns same structure as classify_complaint_from_image.
    """
    client = get_gemini_client()
    if not client:
        return {
            "success": False,
            "category_id": None,
            "error": "GEMINI_API_KEY not configured",
            "message": "Please select category manually"
        }
    
    try:
        categories_list = "\n".join([f"- {cid}: {CATEGORY_NAMES[cid]}" for cid in CATEGORY_OPTIONS])
        
        prompt = f"""Classify this civic complaint into a category.

Complaint Title: {title}
Description: {description}

Available categories:
{categories_list}

Respond in this exact JSON format:
{{
    "category_id": "<category_id from list>",
    "confidence": <0.0 to 1.0>,
    "suggested_urgency": "<low|medium|high|critical>",
    "reasoning": "<why this category>"
}}

Only respond with valid JSON, no other text."""

        response = client.models.generate_content(
            model=GEMINI_MODEL,
            contents=prompt
        )
        
        text = response.text.strip()
        if text.startswith("```"):
            text = text.split("\n", 1)[1].rsplit("```", 1)[0]
        
        result = json.loads(text)
        result["success"] = True
        result["category_name"] = CATEGORY_NAMES.get(result.get("category_id"), "Unknown")
        return result
        
    except Exception as e:
        return {
            "success": False,
            "category_id": None,
            "error": str(e),
            "message": "Please select category manually or configure GEMINI_API_KEY"
        }


async def extract_location_from_text(text: str) -> Optional[Dict[str, str]]:
    """
    Use Gemini to extract location information from complaint text.
    
    Returns:
        {
            "address": "MG Road near Metro Station",
            "locality": "Connaught Place",
            "landmark": "Near Rajiv Chowk Metro"
        }
    """
    client = get_gemini_client()
    if not client:
        return None
    
    try:
        prompt = f"""Extract location information from this complaint text. Focus on Delhi NCR locations.

Text: {text}

Respond in this exact JSON format:
{{
    "address": "<full address if mentioned>",
    "locality": "<area/locality name>",
    "landmark": "<nearby landmark if mentioned>",
    "has_location": <true if location found, false otherwise>
}}

Only respond with valid JSON, no other text."""

        response = client.models.generate_content(
            model=GEMINI_MODEL,
            contents=prompt
        )
        
        text = response.text.strip()
        if text.startswith("```"):
            text = text.split("\n", 1)[1].rsplit("```", 1)[0]
        
        return json.loads(text)
        
    except Exception as e:
        return None


async def analyze_complaint_severity(
    title: str,
    description: str,
    category_id: str,
    image_url: Optional[str] = None
) -> Dict[str, Any]:
    """
    Use Gemini to analyze complaint severity and urgency.
    
    Returns:
        {
            "urgency": "high",
            "severity_score": 0.8,
            "is_emergency": False,
            "reasoning": "..."
        }
    """
    client = get_gemini_client()
    if not client:
        return {"urgency": "medium", "success": False, "fallback": True}
    
    try:
        prompt = f"""Analyze the severity and urgency of this civic complaint.

Title: {title}
Description: {description}
Category: {CATEGORY_NAMES.get(category_id, category_id)}

Consider:
- Safety hazards (traffic, pedestrians, water/electricity)
- Impact on daily life
- Number of people affected
- Time-sensitivity

Respond in this exact JSON format:
{{
    "urgency": "<low|medium|high|critical>",
    "severity_score": <0.0 to 1.0>,
    "is_emergency": <true|false>,
    "requires_immediate_action": <true|false>,
    "reasoning": "<brief explanation>"
}}

Only respond with valid JSON, no other text."""

        response = client.models.generate_content(
            model=GEMINI_MODEL,
            contents=prompt
        )
        
        text = response.text.strip()
        if text.startswith("```"):
            text = text.split("\n", 1)[1].rsplit("```", 1)[0]
        
        result = json.loads(text)
        result["success"] = True
        return result
        
    except Exception as e:
        return {"urgency": "medium", "success": False, "error": str(e), "fallback": True}
