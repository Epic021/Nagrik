"""
AI/ML Integration Routes

These routes allow AI services to interact with complaints and
provide endpoints for querying AI-enriched data.
"""

from typing import Optional, List, Dict, Any
from fastapi import APIRouter, HTTPException, Query, status

from ..core.database import get_db
from ..services.ai_interface import (
    AIServiceRegistry,
    ComplaintAnalysisRequest,
    LocationValidationRequest,
    KnowledgeGraphQuery
)

router = APIRouter(prefix="/ai", tags=["AI/ML Integration"])


@router.post("/analyze/{complaint_id}")
async def analyze_complaint(complaint_id: str):
    """
    Trigger AI analysis on a complaint.
    
    This is called after complaint creation to:
    - Get department suggestion from RAG Engine
    - Extract entities via Context Engine
    - Find similar complaints via Similarity Engine
    - Add to Knowledge Graph
    
    Returns the AI analysis results.
    """
    db = get_db()
    from bson import ObjectId
    
    complaint = await db.complaints.find_one({"_id": ObjectId(complaint_id)})
    if not complaint:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Complaint not found")
    
    # Build analysis request
    request = ComplaintAnalysisRequest(
        complaint_id=complaint_id,
        title=complaint["title"],
        description=complaint["description"],
        category_id=complaint["category"]["id"],
        location={"lat": complaint["location"]["lat"], "lng": complaint["location"]["lng"]},
        media_urls=complaint.get("media_urls", [])
    )
    
    # Run through AI services
    rag_engine = AIServiceRegistry.get_rag_engine()
    result = await rag_engine.analyze_complaint(request)
    
    # Get similar complaints
    similarity_engine = AIServiceRegistry.get_similarity_engine()
    similar_ids = await similarity_engine.get_similar_complaints(complaint_id)
    
    # Add to knowledge graph
    kg = AIServiceRegistry.get_knowledge_graph()
    kg_entity_id = await kg.add_complaint_node(complaint_id, {
        "title": complaint["title"],
        "category": complaint["category"]["id"],
        "location": complaint["location"],
        "department": complaint["department"]["id"]
    })
    
    # Update complaint with AI metadata
    ai_metadata = {
        "kg_entity_id": kg_entity_id,
        "related_complaint_ids": similar_ids[:5],
        "suggested_department_id": result.suggested_department_id,
        "suggested_urgency": result.suggested_urgency,
        "confidence_score": result.confidence_score,
        "similarity_cluster_id": result.similarity_cluster_id
    }
    
    await db.complaints.update_one(
        {"_id": ObjectId(complaint_id)},
        {"$set": {"ai_metadata": ai_metadata}}
    )
    
    return {
        "complaint_id": complaint_id,
        "kg_entity_id": kg_entity_id,
        "suggested_department": result.suggested_department_id,
        "suggested_urgency": result.suggested_urgency,
        "confidence": result.confidence_score,
        "similar_complaints": similar_ids[:5],
        "message": "AI analysis complete"
    }


@router.get("/similar/{complaint_id}")
async def get_similar_complaints(
    complaint_id: str,
    limit: int = Query(5, ge=1, le=20)
):
    """Get complaints similar to the given complaint."""
    similarity_engine = AIServiceRegistry.get_similarity_engine()
    similar_ids = await similarity_engine.get_similar_complaints(complaint_id, limit)
    
    if not similar_ids:
        return {"similar_complaints": []}
    
    # Fetch complaint details
    db = get_db()
    from bson import ObjectId
    
    complaints = []
    for sid in similar_ids:
        try:
            doc = await db.complaints.find_one({"_id": ObjectId(sid)})
            if doc:
                complaints.append({
                    "id": str(doc["_id"]),
                    "title": doc["title"],
                    "category": doc["category"]["name"],
                    "status": doc["status"],
                    "upvotes": doc.get("upvote_count", 0)
                })
        except:
            continue
    
    return {"similar_complaints": complaints}


@router.get("/knowledge-graph/related/{entity_id}")
async def get_related_entities(
    entity_id: str,
    entity_type: str = Query("complaint"),
    depth: int = Query(1, ge=1, le=3)
):
    """
    Query the knowledge graph for related entities.
    
    Use this to find:
    - Complaints related to a location
    - Complaints handled by a department
    - Resolution patterns
    """
    kg = AIServiceRegistry.get_knowledge_graph()
    
    query = KnowledgeGraphQuery(
        entity_type=entity_type,
        entity_id=entity_id,
        depth=depth
    )
    
    result = await kg.query(query)
    
    return {
        "entity_id": entity_id,
        "entity_type": entity_type,
        "nodes": result.nodes,
        "edges": result.edges
    }


@router.get("/hotspots")
async def get_complaint_hotspots(
    lat: float = Query(...),
    lng: float = Query(...),
    radius_km: float = Query(5, ge=0.5, le=50)
):
    """
    Get complaint hotspots from the knowledge graph.
    
    Hotspots are areas with recurring issues, useful for
    predictive maintenance and resource allocation.
    """
    kg = AIServiceRegistry.get_knowledge_graph()
    hotspots = await kg.get_hotspots(lat, lng, radius_km)
    
    return {"hotspots": hotspots}


@router.post("/validate-location")
async def validate_location(request: LocationValidationRequest):
    """
    Validate and enrich location data using Google Maps.
    
    Returns normalized address, locality, ward info.
    """
    validator = AIServiceRegistry.get_location_validator()
    result = await validator.validate_location(request)
    
    return {
        "is_valid": result.is_valid,
        "normalized_address": result.normalized_address,
        "locality": result.locality,
        "district": result.district,
        "pincode": result.pincode,
        "ward": result.ward
    }


@router.post("/geocode")
async def geocode_address(address: str = Query(...)):
    """Convert address to coordinates using Google Maps Geocoding."""
    validator = AIServiceRegistry.get_location_validator()
    coords = await validator.geocode_address(address)
    
    if not coords:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Could not geocode address"
        )
    
    return coords


# === Internal endpoints for AI services to update data ===

@router.put("/complaints/{complaint_id}/ai-metadata")
async def update_ai_metadata(
    complaint_id: str,
    metadata: Dict[str, Any]
):
    """
    Update AI metadata for a complaint.
    
    Called by AI services when analysis is complete.
    """
    db = get_db()
    from bson import ObjectId
    
    result = await db.complaints.update_one(
        {"_id": ObjectId(complaint_id)},
        {"$set": {"ai_metadata": metadata}}
    )
    
    if result.matched_count == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Complaint not found")
    
    return {"message": "AI metadata updated", "complaint_id": complaint_id}


@router.post("/complaints/{complaint_id}/link")
async def link_complaint_to_entity(
    complaint_id: str,
    target_id: str = Query(..., description="Target entity ID"),
    relationship: str = Query(..., description="Relationship type: similar_to, duplicate_of, located_at")
):
    """
    Link a complaint to another entity in the knowledge graph.
    
    Relationship types:
    - similar_to: Complaints about similar issues
    - duplicate_of: Confirmed duplicate
    - located_at: Link to location entity
    - assigned_to: Link to department entity
    """
    kg = AIServiceRegistry.get_knowledge_graph()
    success = await kg.link_entities(complaint_id, target_id, relationship)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create link"
        )
    
    return {
        "message": "Link created",
        "from": complaint_id,
        "to": target_id,
        "relationship": relationship
    }
