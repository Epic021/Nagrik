from datetime import datetime, timezone
from typing import Optional, List
from bson import ObjectId

from ..core.database import get_db
from ..models.complaints import (
    ComplaintCreate, ComplaintResponse, ComplaintStatus,
    CategoryRef, DepartmentRef, UserRef, GeoLocation
)
from .deduplication import find_duplicate_complaint, merge_into_existing
from .google_services import geocode_address
from .gemini_ai import extract_location_from_text


async def _get_category_from_db(category_id: str):
    """Look up category from the database."""
    db = get_db()
    try:
        from bson import ObjectId as ObjId
        cat = await db.categories.find_one({"_id": ObjId(category_id)})
        if cat:
            return {
                "id": str(cat["_id"]),
                "name": cat["name"],
                "default_department_id": cat.get("default_department_id")
            }
    except:
        pass
    return None


async def _get_department_from_db(department_id):
    """Look up department from the database. Accepts ObjectId or string."""
    db = get_db()
    try:
        from bson import ObjectId as ObjId
        if not isinstance(department_id, ObjId):
            department_id = ObjId(department_id)
        dept = await db.departments.find_one({"_id": department_id})
        if dept:
            return {
                "id": str(dept["_id"]),
                "name": dept.get("full_name", dept.get("name", "Unknown")),
                "short_name": dept.get("name", dept.get("short_name", "?"))
            }
    except:
        pass
    return None


async def create_complaint(
    complaint_data: ComplaintCreate,
    user_id: str,
    user_name: str
) -> tuple[ComplaintResponse, bool, Optional[str]]:
    """
    Create a new complaint or merge into existing duplicate.
    
    Returns:
        (complaint, is_new, duplicate_id)
        - If new complaint created: (complaint, True, None)
        - If merged into existing: (existing_complaint, False, existing_id)
    """
    db = get_db()
    
    # Check for duplicates first
    duplicate_id = await find_duplicate_complaint(
        category_id=complaint_data.category_id,
        lat=complaint_data.location.lat,
        lng=complaint_data.location.lng,
        title=complaint_data.title,
        description=complaint_data.description
    )
    
    if duplicate_id:
        # Merge into existing by upvoting
        await merge_into_existing(duplicate_id, user_id)
        existing = await get_complaint_by_id(duplicate_id, user_id)
        return existing, False, duplicate_id
    
    # Get category and department from database
    category = await _get_category_from_db(complaint_data.category_id)
    if not category:
        raise ValueError(f"Invalid category: {complaint_data.category_id}")
    
    department = await _get_department_from_db(category["default_department_id"])
    if not department:
        raise ValueError(f"Department not found for category: {complaint_data.category_id}")
    
    now = datetime.now(timezone.utc)
    
    # Automated Geocoding if coordinates are missing/zero
    location_data = complaint_data.location
    if (location_data.lat == 0 and location_data.lng == 0):
        # Use existing address if available
        query = location_data.address
        
        # If no address, try to extract from title + description using Gemini
        if not query:
            print(f"[GEO] Using Gemini to extract location from text...")
            extracted = await extract_location_from_text(f"{complaint_data.title} {complaint_data.description}")
            if extracted and extracted.get("has_location"):
                query = extracted.get("address") or extracted.get("locality")
                if query:
                    location_data.address = query
                    print(f"[GEO] Gemini extracted: {query}")
        
        if query:
            # Add context for better geocoding if it's a short query
            geocode_query = query if "Delhi" in query else f"{query} Delhi"
            print(f"[GEO] Attempting background geocoding for: {geocode_query}")
            geo_result = await geocode_address(geocode_query)
            if geo_result:
                location_data.lat = geo_result["lat"]
                location_data.lng = geo_result["lng"]
                print(f"[GEO] Success: {location_data.lat}, {location_data.lng}")
    
    geo_location = location_data.to_geojson()
    
    complaint_doc = {
        "title": complaint_data.title,
        "description": complaint_data.description,
        "category": {"id": category["id"], "name": category["name"]},
        "department": {"id": department["id"], "name": department["name"], "short_name": department["short_name"]},
        "location": location_data.model_dump(),
        "geo_location": geo_location.model_dump(),
        "media_urls": complaint_data.media_urls,
        "urgency": complaint_data.urgency.value,
        "status": ComplaintStatus.PENDING.value,
        "upvote_count": 1,  # Creator auto-upvotes
        "upvoters": [user_id],
        "duplicate_of": None,
        "created_by": {"id": user_id, "name": user_name},
        "created_at": now,
        "updated_at": now,
        "resolved_at": None,
        "resolution_notes": None,
        "citizen_verified": None
    }
    
    result = await db.complaints.insert_one(complaint_doc)
    complaint_doc["_id"] = result.inserted_id
    
    return _doc_to_response(complaint_doc, user_id), True, None


async def get_complaint_by_id(complaint_id: str, user_id: Optional[str] = None) -> Optional[ComplaintResponse]:
    """Get complaint by ID."""
    db = get_db()
    try:
        doc = await db.complaints.find_one({"_id": ObjectId(complaint_id)})
        if doc:
            return _doc_to_response(doc, user_id)
        return None
    except:
        return None


async def list_complaints(
    category_id: Optional[str] = None,
    department_id: Optional[str] = None,
    status: Optional[str] = None,
    lat: Optional[float] = None,
    lng: Optional[float] = None,
    radius_km: float = 10,
    page: int = 1,
    limit: int = 20,
    sort_by: str = "created_at",
    user_id: Optional[str] = None
) -> tuple[List[ComplaintResponse], int]:
    """
    List complaints with filters.
    Returns (complaints, total_count).
    """
    db = get_db()
    
    query = {}
    
    if category_id:
        query["category.id"] = category_id
    if department_id:
        query["department.id"] = department_id
    if status:
        query["status"] = status
    
    # Geo query if location provided
    if lat is not None and lng is not None:
        query["geo_location"] = {
            "$near": {
                "$geometry": {"type": "Point", "coordinates": [lng, lat]},
                "$maxDistance": radius_km * 1000  # Convert to meters
            }
        }
    
    # Sort options
    sort_mapping = {
        "created_at": [("created_at", -1)],
        "upvotes": [("upvote_count", -1), ("created_at", -1)],
        "urgency": [("urgency", -1), ("created_at", -1)]
    }
    sort = sort_mapping.get(sort_by, [("created_at", -1)])
    
    # Get total count
    total = await db.complaints.count_documents(query)
    
    # Get paginated results
    skip = (page - 1) * limit
    cursor = db.complaints.find(query).sort(sort).skip(skip).limit(limit)
    docs = await cursor.to_list(length=limit)
    
    complaints = [_doc_to_response(doc, user_id) for doc in docs]
    
    return complaints, total


async def get_user_complaints(user_id: str, page: int = 1, limit: int = 20) -> tuple[List[ComplaintResponse], int]:
    """Get complaints created by a user."""
    db = get_db()
    
    query = {"created_by.id": user_id}
    total = await db.complaints.count_documents(query)
    
    skip = (page - 1) * limit
    cursor = db.complaints.find(query).sort("created_at", -1).skip(skip).limit(limit)
    docs = await cursor.to_list(length=limit)
    
    complaints = [_doc_to_response(doc, user_id) for doc in docs]
    return complaints, total


async def upvote_complaint(complaint_id: str, user_id: str) -> bool:
    """Add upvote to complaint. Returns True if successful."""
    db = get_db()
    result = await db.complaints.update_one(
        {"_id": ObjectId(complaint_id), "upvoters": {"$ne": user_id}},
        {"$push": {"upvoters": user_id}, "$inc": {"upvote_count": 1}}
    )
    return result.modified_count > 0


async def remove_upvote(complaint_id: str, user_id: str) -> bool:
    """Remove upvote from complaint. Returns True if successful."""
    db = get_db()
    result = await db.complaints.update_one(
        {"_id": ObjectId(complaint_id), "upvoters": user_id},
        {"$pull": {"upvoters": user_id}, "$inc": {"upvote_count": -1}}
    )
    return result.modified_count > 0


async def verify_resolution(complaint_id: str, user_id: str, accepted: bool, feedback: Optional[str] = None) -> bool:
    """
    Citizen verifies if resolution is satisfactory.
    Only the complaint creator can verify.
    """
    db = get_db()
    
    update = {
        "$set": {
            "citizen_verified": accepted,
            "updated_at": datetime.now(timezone.utc)
        }
    }
    
    if not accepted:
        update["$set"]["status"] = ComplaintStatus.CITIZEN_REJECTED.value
        if feedback:
            update["$set"]["resolution_feedback"] = feedback
    
    result = await db.complaints.update_one(
        {
            "_id": ObjectId(complaint_id),
            "created_by.id": user_id,
            "status": ComplaintStatus.RESOLVED.value
        },
        update
    )
    return result.modified_count > 0


def _doc_to_response(doc: dict, user_id: Optional[str] = None) -> ComplaintResponse:
    """Convert MongoDB document to response model."""
    from ..models.complaints import Location, Urgency
    
    # Handle location field name differences (lat/lng vs latitude/longitude)
    loc_data = doc.get("location", {})
    if loc_data:
        if "lat" not in loc_data and "latitude" in loc_data:
            loc_data = {
                "lat": loc_data["latitude"],
                "lng": loc_data["longitude"],
                "address": loc_data.get("address")
            }
    else:
        loc_data = {"lat": 0, "lng": 0}
    
    # Handle missing created_by
    created_by_data = doc.get("created_by")
    if not created_by_data:
        created_by_data = {"id": "unknown", "name": "Anonymous"}
    
    return ComplaintResponse(
        id=str(doc["_id"]),
        title=doc.get("title", ""),
        description=doc.get("description", ""),
        category=CategoryRef(**doc.get("category", {"id": "unknown", "name": "Unknown"})),
        department=DepartmentRef(**doc.get("department", {"id": "unknown", "name": "Unknown"})),
        location=Location(**loc_data),
        media_urls=doc.get("media_urls", []),
        urgency=Urgency(doc.get("urgency", "normal")),
        status=ComplaintStatus(doc.get("status", "pending")),
        upvote_count=doc.get("upvote_count", 0),
        has_upvoted=user_id in doc.get("upvoters", []) if user_id else False,
        created_by=UserRef(**created_by_data),
        created_at=doc.get("created_at"),
        resolved_at=doc.get("resolved_at"),
        citizen_verified=doc.get("citizen_verified")
    )
