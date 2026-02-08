"""
WhatsApp Bot Service - Full Complaint Registration

This module handles:
1. Conversational state machine for complaint collection
2. Gemini AI for classification and responses
3. MongoDB integration for saving complaints
"""

import traceback
from datetime import datetime, timezone
from typing import Optional, Dict, List, Any
from bson import ObjectId

from ..core.config import get_settings
from ..core.database import get_db
from ..models.departments import get_category_by_id, get_department_by_id, COMPLAINT_CATEGORIES

settings = get_settings()

# Gemini model
GEMINI_MODEL = "gemini-2.0-flash"

# Conversation states
STATE_IDLE = "idle"
STATE_COLLECTING = "collecting"
STATE_AWAITING_LOCATION = "awaiting_location"
STATE_CONFIRMING = "confirming"

# System prompt for Gemini
SYSTEM_PROMPT = """You are NAGRIK Bot - a helpful assistant for Delhi's civic complaint platform.

Your role:
1. Help users describe their civic issue clearly
2. Ask clarifying questions if the description is vague
3. Identify the category from: Potholes, Road Damage, Garbage, Sanitation, Street Lights, Water Supply, Drainage, Electricity, Traffic, Encroachment, Noise/Air Pollution, Parks, Footpaths, Public Safety
4. Assess urgency (low/medium/high/critical)
5. Be concise and professional

When you have enough information, end your response with:
[READY_TO_REGISTER]

Otherwise, ask the next relevant question. Maximum 2-3 sentences per response."""


def get_gemini_client():
    """Get Gemini client with API key."""
    if not settings.GEMINI_API_KEY:
        return None
    from google import genai
    return genai.Client(api_key=settings.GEMINI_API_KEY)


class ConversationSession:
    """Tracks a single user's complaint session."""
    
    def __init__(self):
        self.state = STATE_IDLE
        self.messages: List[Dict] = []
        self.description = ""
        self.category_id = None
        self.urgency = "medium"
        self.location_address = None
        self.location_lat = 28.6139  # Default Delhi
        self.location_lng = 77.2090
        self.image_base64 = None
        self.updated_at = datetime.now(timezone.utc)


# In-memory sessions (could migrate to Redis for production)
sessions: Dict[str, ConversationSession] = {}


def get_session(user_id: str) -> ConversationSession:
    """Get or create session for user."""
    if user_id not in sessions:
        sessions[user_id] = ConversationSession()
    sessions[user_id].updated_at = datetime.now(timezone.utc)
    return sessions[user_id]


async def classify_with_gemini(text: str) -> Dict[str, Any]:
    """Use Gemini to classify complaint category and urgency."""
    client = get_gemini_client()
    if not client:
        return {"category_id": "other", "urgency": "medium"}
    
    try:
        categories_list = ", ".join([f"{c.id}:{c.name}" for c in COMPLAINT_CATEGORIES])
        prompt = f"""Classify this complaint and return ONLY a JSON object:

Complaint: {text}

Categories: {categories_list}

Return format (no other text):
{{"category_id": "<id>", "urgency": "<low|medium|high|critical>"}}"""

        response = client.models.generate_content(model=GEMINI_MODEL, contents=prompt)
        import json
        result_text = response.text.strip()
        if result_text.startswith("```"):
            result_text = result_text.split("\n", 1)[1].rsplit("```", 1)[0]
        return json.loads(result_text)
    except:
        return {"category_id": "other", "urgency": "medium"}


async def generate_chat_response(
    user_id: str,
    message: str = "",
    image_base64: Optional[str] = None
) -> Dict[str, Any]:
    """
    Process user message and generate response.
    Manages conversation flow and complaint registration.
    """
    try:
        session = get_session(user_id)
        db = get_db()
        
        # Store image if provided
        if image_base64:
            session.image_base64 = image_base64
        
        # Clean phone from WhatsApp JID
        phone = user_id.split("@")[0]
        if phone.startswith("91") and len(phone) > 10:
            phone = phone[2:]
        
        # === STATE: IDLE - Start collecting ===
        if session.state == STATE_IDLE:
            session.state = STATE_COLLECTING
            session.description = message
            session.messages.append({"role": "user", "content": message})
            
            # Get initial classification
            classification = await classify_with_gemini(message)
            session.category_id = classification.get("category_id", "other")
            session.urgency = classification.get("urgency", "medium")
            
            category = get_category_by_id(session.category_id)
            cat_name = category.name if category else "General"
            
            response = f"Thanks for reporting this issue.\n\nCategory: *{cat_name}*\nUrgency: *{session.urgency}*\n\nPlease share the location (type the address or area name):"
            session.state = STATE_AWAITING_LOCATION
            
            return {"response": response, "success": True}
        
        # === STATE: AWAITING LOCATION ===
        elif session.state == STATE_AWAITING_LOCATION:
            session.location_address = message
            session.messages.append({"role": "user", "content": f"Location: {message}"})
            
            # Geocode the address using Google Maps API
            from .google_services import geocode_address, validate_delhi_location
            
            geocode_result = await geocode_address(message)
            if geocode_result:
                session.location_lat = geocode_result["lat"]
                session.location_lng = geocode_result["lng"]
                
                # Validate it's in Delhi
                is_delhi = validate_delhi_location(session.location_lat, session.location_lng)
                if not is_delhi:
                    return {
                        "response": f"The location '{message}' seems to be outside Delhi NCR.\n\nPlease provide a location within Delhi (e.g., Connaught Place, Lajpat Nagar, Dwarka):",
                        "success": True
                    }
            else:
                # Geocoding failed, use default Delhi coords but warn user
                session.location_lat = 28.6139
                session.location_lng = 77.2090
            
            # Prepare confirmation
            category = get_category_by_id(session.category_id)
            cat_name = category.name if category else "Other"
            dept = get_department_by_id(category.default_department_id if category else "mcd")
            dept_name = dept.name if dept else "MCD"
            
            coords_info = ""
            if geocode_result:
                coords_info = f"\nCoordinates: {session.location_lat:.4f}, {session.location_lng:.4f}"
            
            summary = f"""*Confirm your complaint:*

Issue: {session.description[:150]}...
Category: {cat_name}
Department: {dept_name}
Location: {session.location_address}{coords_info}
Urgency: {session.urgency}

Reply *YES* to submit or *NO* to cancel."""
            
            session.state = STATE_CONFIRMING
            return {"response": summary, "success": True}
        
        # === STATE: CONFIRMING ===
        elif session.state == STATE_CONFIRMING:
            if message.upper() in ["YES", "Y", "CONFIRM", "OK", "SUBMIT"]:
                # Create complaint in MongoDB
                try:
                    # Get or create user
                    user = await db.users.find_one({"phone": phone})
                    if not user:
                        from ..services.users import hash_password
                        result = await db.users.insert_one({
                            "name": f"WhatsApp User ({phone[-4:]})",
                            "phone": phone,
                            "password_hash": hash_password(f"wa_{phone}_{datetime.now().timestamp()}"),
                            "role": "citizen",
                            "department_id": None,
                            "created_at": datetime.now(timezone.utc),
                            "updated_at": datetime.now(timezone.utc)
                        })
                        user = {"_id": result.inserted_id, "name": f"WhatsApp User ({phone[-4:]})"}
                    
                    category = get_category_by_id(session.category_id) or COMPLAINT_CATEGORIES[-1]
                    department = get_department_by_id(category.default_department_id)
                    
                    complaint_doc = {
                        "title": session.description[:100],
                        "description": session.description,
                        "category": {"id": category.id, "name": category.name},
                        "department": {
                            "id": department.id if department else "mcd",
                            "name": department.name if department else "MCD",
                            "short_name": department.short_name if department else "MCD"
                        },
                        "location": {
                            "lat": session.location_lat,
                            "lng": session.location_lng,
                            "address": session.location_address or "Delhi"
                        },
                        "geo_location": {
                            "type": "Point",
                            "coordinates": [session.location_lng, session.location_lat]
                        },
                        "media_urls": [],
                        "urgency": session.urgency,
                        "status": "pending",
                        "upvote_count": 1,
                        "upvoters": [str(user["_id"])],
                        "created_by": {"id": str(user["_id"]), "name": user.get("name", "User")},
                        "source": "whatsapp",
                        "created_at": datetime.now(timezone.utc),
                        "updated_at": datetime.now(timezone.utc)
                    }
                    
                    result = await db.complaints.insert_one(complaint_doc)
                    complaint_id = str(result.inserted_id)
                    
                    # Reset session
                    sessions[user_id] = ConversationSession()
                    
                    return {
                        "response": f"Complaint Registered!\n\nID: {complaint_id}\nCategory: {category.name}\nDept: {department.name if department else 'MCD'}\n\nTrack at: nagrik.delhi.gov.in\n\nType START for a new complaint.",
                        "success": True
                    }
                    
                except Exception as e:
                    traceback.print_exc()
                    return {
                        "response": f"Error saving complaint. Please try again.\n\nDetails: {str(e)[:80]}",
                        "success": False,
                        "error": str(e)
                    }
            
            elif message.upper() in ["NO", "N", "CANCEL"]:
                sessions[user_id] = ConversationSession()
                return {
                    "response": "Complaint cancelled.\n\nType START to begin a new complaint.",
                    "success": True
                }
            
            else:
                return {
                    "response": "Please reply *YES* to submit or *NO* to cancel.",
                    "success": True
                }
        
        # === STATE: COLLECTING (additional details) ===
        elif session.state == STATE_COLLECTING:
            session.description += " " + message
            session.messages.append({"role": "user", "content": message})
            
            # Re-classify with more info
            classification = await classify_with_gemini(session.description)
            session.category_id = classification.get("category_id", session.category_id)
            session.urgency = classification.get("urgency", session.urgency)
            
            session.state = STATE_AWAITING_LOCATION
            return {
                "response": "Got it. Now please share the location (address or area name):",
                "success": True
            }
        
        # Fallback
        else:
            sessions[user_id] = ConversationSession()
            return {
                "response": "Session reset. Please describe your complaint to begin.",
                "success": True
            }
            
    except Exception as e:
        traceback.print_exc()
        return {
            "response": "Sorry, something went wrong. Please try again.",
            "success": False,
            "error": str(e)
        }


async def clear_session(user_id: str) -> Dict[str, Any]:
    """Clear user's conversation session."""
    if user_id in sessions:
        del sessions[user_id]
        return {"success": True, "message": "Session cleared"}
    return {"success": True, "message": "No session found"}


def get_active_sessions_count() -> int:
    """Get count of active sessions."""
    return len(sessions)
