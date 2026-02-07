from typing import List, Optional
from fastapi import APIRouter, Query
from pydantic import BaseModel

from ..core.database import get_db
from ..models.departments import DELHI_DEPARTMENTS, DepartmentStats

router = APIRouter(prefix="/leaderboards", tags=["Leaderboards"])


class DepartmentLeaderboardResponse(BaseModel):
    rankings: List[DepartmentStats]
    period: str


class IssueRanking(BaseModel):
    rank: int
    complaint_id: str
    title: str
    category: str
    upvotes: int
    status: str
    lat: float
    lng: float
    address: Optional[str] = None


class TopIssuesResponse(BaseModel):
    top_issues: List[IssueRanking]
    area: Optional[str] = None


class HotspotLocation(BaseModel):
    lat: float
    lng: float
    address: Optional[str] = None
    complaint_count: int
    top_categories: List[str]


class HotspotsResponse(BaseModel):
    hotspots: List[HotspotLocation]


@router.get("/departments", response_model=DepartmentLeaderboardResponse)
async def get_department_leaderboard():
    """
    Get departments ranked by performance.
    
    Score is calculated based on:
    - Resolution rate (% of complaints resolved)
    - Average resolution time
    - Citizen verification rate (% of resolutions accepted by citizens)
    """
    db = get_db()
    
    rankings = []
    
    for dept in DELHI_DEPARTMENTS:
        # Get stats for this department
        total = await db.complaints.count_documents({"department.id": dept.id})
        resolved = await db.complaints.count_documents({
            "department.id": dept.id,
            "status": "resolved"
        })
        pending = await db.complaints.count_documents({
            "department.id": dept.id,
            "status": "pending"
        })
        in_progress = await db.complaints.count_documents({
            "department.id": dept.id,
            "status": "in_progress"
        })
        
        # Calculate resolution rate
        resolution_rate = (resolved / total * 100) if total > 0 else 0
        
        # Calculate citizen satisfaction (verified resolutions)
        citizen_verified = await db.complaints.count_documents({
            "department.id": dept.id,
            "status": "resolved",
            "citizen_verified": True
        })
        citizen_rejected = await db.complaints.count_documents({
            "department.id": dept.id,
            "status": "citizen_rejected"
        })
        
        satisfaction_rate = 0
        if resolved > 0:
            satisfaction_rate = (citizen_verified / (citizen_verified + citizen_rejected) * 100) if (citizen_verified + citizen_rejected) > 0 else 50
        
        # Calculate overall score (weighted)
        score = (resolution_rate * 0.6) + (satisfaction_rate * 0.4)
        
        rankings.append(DepartmentStats(
            id=dept.id,
            name=dept.name,
            short_name=dept.short_name,
            total_complaints=total,
            resolved=resolved,
            pending=pending,
            in_progress=in_progress,
            resolution_rate=round(resolution_rate, 1),
            avg_resolution_hours=None,  # TODO: Calculate from resolved_at - created_at
            score=round(score, 1)
        ))
    
    # Sort by score descending
    rankings.sort(key=lambda x: x.score, reverse=True)
    
    return DepartmentLeaderboardResponse(rankings=rankings, period="all_time")


@router.get("/issues", response_model=TopIssuesResponse)
async def get_top_issues(
    lat: Optional[float] = Query(None, description="Center latitude"),
    lng: Optional[float] = Query(None, description="Center longitude"),
    radius: float = Query(10, description="Radius in km"),
    limit: int = Query(10, ge=1, le=50)
):
    """Get top issues by upvotes, optionally filtered by location."""
    db = get_db()
    
    query = {"status": {"$nin": ["resolved", "rejected"]}}
    
    # Add geo filter if location provided
    if lat is not None and lng is not None:
        query["geo_location"] = {
            "$near": {
                "$geometry": {"type": "Point", "coordinates": [lng, lat]},
                "$maxDistance": radius * 1000
            }
        }
    
    cursor = db.complaints.find(query).sort("upvote_count", -1).limit(limit)
    docs = await cursor.to_list(length=limit)
    
    top_issues = []
    for i, doc in enumerate(docs, 1):
        top_issues.append(IssueRanking(
            rank=i,
            complaint_id=str(doc["_id"]),
            title=doc["title"],
            category=doc["category"]["name"],
            upvotes=doc.get("upvote_count", 0),
            status=doc["status"],
            lat=doc["location"]["lat"],
            lng=doc["location"]["lng"],
            address=doc["location"].get("address")
        ))
    
    return TopIssuesResponse(top_issues=top_issues)


@router.get("/hotspots", response_model=HotspotsResponse)
async def get_hotspots(
    lat: Optional[float] = Query(None),
    lng: Optional[float] = Query(None),
    radius: float = Query(20),
    limit: int = Query(10, ge=1, le=20)
):
    """
    Get locations with most complaints (hotspots).
    Uses MongoDB aggregation to cluster nearby complaints.
    """
    db = get_db()
    
    # Simple approach: get top complained areas
    # Group by approximate location (rounded to 3 decimal places ~100m precision)
    pipeline = [
        {"$match": {"status": {"$nin": ["resolved", "rejected"]}}},
        {"$group": {
            "_id": {
                "lat": {"$round": ["$location.lat", 3]},
                "lng": {"$round": ["$location.lng", 3]}
            },
            "count": {"$sum": 1},
            "address": {"$first": "$location.address"},
            "categories": {"$push": "$category.name"}
        }},
        {"$sort": {"count": -1}},
        {"$limit": limit}
    ]
    
    results = await db.complaints.aggregate(pipeline).to_list(length=limit)
    
    hotspots = []
    for r in results:
        # Get top 3 categories
        category_counts = {}
        for cat in r["categories"]:
            category_counts[cat] = category_counts.get(cat, 0) + 1
        top_cats = sorted(category_counts.keys(), key=lambda x: category_counts[x], reverse=True)[:3]
        
        hotspots.append(HotspotLocation(
            lat=r["_id"]["lat"],
            lng=r["_id"]["lng"],
            address=r.get("address"),
            complaint_count=r["count"],
            top_categories=top_cats
        ))
    
    return HotspotsResponse(hotspots=hotspots)
