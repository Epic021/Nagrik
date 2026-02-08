"""
Complaint deduplication service using location + category + text similarity.
If a similar complaint exists within radius, auto-upvotes instead of creating new.
"""
from difflib import SequenceMatcher
from typing import Optional

from ..core.database import get_db


# Deduplication settings
DUPLICATE_RADIUS_METERS = 200  # Within 200m
TITLE_SIMILARITY_THRESHOLD = 0.6
DESCRIPTION_SIMILARITY_THRESHOLD = 0.5


def text_similarity(text1: str, text2: str) -> float:
    """Calculate similarity ratio between two texts."""
    return SequenceMatcher(None, text1.lower(), text2.lower()).ratio()


async def find_duplicate_complaint(
    category_id: str,
    lat: float,
    lng: float,
    title: str,
    description: str,
    exclude_statuses: list = None
) -> Optional[str]:
    """
    Find a potential duplicate complaint.
    
    Returns complaint_id if duplicate found, None otherwise.
    
    Criteria:
    1. Same category
    2. Within DUPLICATE_RADIUS_METERS
    3. Title OR description similarity above threshold
    4. Not resolved/rejected
    """
    if exclude_statuses is None:
        exclude_statuses = ["resolved", "rejected", "citizen_rejected"]
    
    db = get_db()
    
    # Find nearby complaints with same category
    nearby_complaints = await db.complaints.find({
        "category.id": category_id,
        "status": {"$nin": exclude_statuses},
        "geo_location": {
            "$near": {
                "$geometry": {
                    "type": "Point",
                    "coordinates": [lng, lat]
                },
                "$maxDistance": DUPLICATE_RADIUS_METERS
            }
        }
    }).limit(10).to_list(length=10)
    
    # Check text similarity
    for complaint in nearby_complaints:
        title_sim = text_similarity(title, complaint.get("title", ""))
        desc_sim = text_similarity(description, complaint.get("description", ""))
        
        if title_sim >= TITLE_SIMILARITY_THRESHOLD or desc_sim >= DESCRIPTION_SIMILARITY_THRESHOLD:
            return str(complaint["_id"])
    
    return None


async def merge_into_existing(
    existing_complaint_id: str,
    user_id: str
) -> bool:
    """
    Merge a new complaint into an existing one by upvoting.
    Returns True if successfully merged.
    """
    db = get_db()
    
    # Add upvote if user hasn't already upvoted
    result = await db.complaints.update_one(
        {
            "_id": existing_complaint_id,
            "upvoters": {"$ne": user_id}
        },
        {
            "$push": {"upvoters": user_id},
            "$inc": {"upvote_count": 1}
        }
    )
    
    return result.modified_count > 0
