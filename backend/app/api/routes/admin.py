"""
Admin Routes - Department Dashboard and Complaint Management

Features:
- Department admin authentication
- View complaints assigned to my department
- Update complaint status
- Mark complaints as resolved
- Department analytics and stats
- Assign complaints to staff
"""
from datetime import datetime, timezone, timedelta
from typing import Optional, List
from enum import Enum
from fastapi import APIRouter, HTTPException, Depends, Query, status
from pydantic import BaseModel, Field
from bson import ObjectId

from ..core.database import get_db
from ..models.users import UserRole
from ..models.complaints import ComplaintStatus
from .auth import get_current_user

router = APIRouter(prefix="/admin", tags=["Admin Dashboard"])


# ============ Models ============

class AdminCreate(BaseModel):
    name: str = Field(..., min_length=2)
    phone: str = Field(..., pattern=r"^[6-9]\d{9}$")
    password: str = Field(..., min_length=6)
    department_id: str  # Required for department admins


class StatusUpdate(BaseModel):
    status: ComplaintStatus
    notes: Optional[str] = None


class ResolutionData(BaseModel):
    resolution_notes: str = Field(..., min_length=10)
    resolved_by_name: Optional[str] = None


class AssignmentData(BaseModel):
    assigned_to_name: str
    assigned_to_phone: Optional[str] = None
    priority: Optional[str] = "normal"  # low, normal, high, urgent


class EscalationData(BaseModel):
    reason: str
    escalate_to: Optional[str] = None  # Higher authority ID


# ============ Auth Helpers ============

async def get_admin_user(user: dict = Depends(get_current_user)):
    """Require department_admin or super_admin role."""
    if user.get("role") not in [UserRole.DEPARTMENT_ADMIN.value, UserRole.SUPER_ADMIN.value, "department_admin", "super_admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return user


async def get_super_admin(user: dict = Depends(get_current_user)):
    """Require super_admin role."""
    if user.get("role") not in [UserRole.SUPER_ADMIN.value, "super_admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Super admin access required"
        )
    return user


# ============ Admin Registration ============

@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register_admin(
    data: AdminCreate,
    current_admin: dict = Depends(get_super_admin)
):
    """
    Register a new department admin.
    Only super admins can create department admins.
    """
    from ..services.users import hash_password
    
    db = get_db()
    
    # Check if phone already exists
    existing = await db.users.find_one({"phone": data.phone})
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Phone number already registered"
        )
    
    # Validate department
    from ..models.departments import get_department_by_id
    department = get_department_by_id(data.department_id)
    if not department:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid department ID"
        )
    
    now = datetime.now(timezone.utc)
    user_doc = {
        "name": data.name,
        "phone": data.phone,
        "password_hash": hash_password(data.password),
        "role": UserRole.DEPARTMENT_ADMIN.value,
        "department_id": data.department_id,
        "created_at": now,
        "updated_at": now
    }
    
    result = await db.users.insert_one(user_doc)
    
    return {
        "id": str(result.inserted_id),
        "name": data.name,
        "phone": data.phone,
        "role": "department_admin",
        "department_id": data.department_id,
        "department_name": department.name
    }


# ============ Department Complaints ============

@router.get("/complaints")
async def get_department_complaints(
    status_filter: Optional[str] = Query(None, alias="status"),
    urgency: Optional[str] = None,
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    sort_by: str = Query("created_at", regex="^(created_at|urgency|upvote_count)$"),
    admin: dict = Depends(get_admin_user)
):
    """
    Get complaints assigned to the admin's department.
    Super admins can see all complaints.
    """
    db = get_db()
    
    query = {}
    
    # Filter by department (unless super admin)
    if admin.get("role") != "super_admin" and admin.get("department_id"):
        query["department.id"] = admin["department_id"]
    
    if status_filter:
        query["status"] = status_filter
    if urgency:
        query["urgency"] = urgency
    
    # Sort
    sort_mapping = {
        "created_at": [("created_at", -1)],
        "urgency": [("urgency", -1), ("created_at", -1)],
        "upvote_count": [("upvote_count", -1)]
    }
    sort = sort_mapping.get(sort_by, [("created_at", -1)])
    
    # Get total
    total = await db.complaints.count_documents(query)
    
    # Paginate
    skip = (page - 1) * limit
    cursor = db.complaints.find(query).sort(sort).skip(skip).limit(limit)
    docs = await cursor.to_list(length=limit)
    
    complaints = []
    for doc in docs:
        complaints.append({
            "id": str(doc["_id"]),
            "title": doc["title"],
            "description": doc["description"],
            "category": doc["category"],
            "department": doc["department"],
            "location": doc.get("location"),
            "urgency": doc["urgency"],
            "status": doc["status"],
            "upvote_count": doc.get("upvote_count", 0),
            "created_by": doc.get("created_by"),
            "created_at": doc["created_at"],
            "assigned_to": doc.get("assigned_to"),
            "resolution_notes": doc.get("resolution_notes"),
            "resolved_at": doc.get("resolved_at")
        })
    
    return {
        "complaints": complaints,
        "total": total,
        "page": page,
        "pages": (total + limit - 1) // limit
    }


@router.get("/complaints/{complaint_id}")
async def get_complaint_detail(
    complaint_id: str,
    admin: dict = Depends(get_admin_user)
):
    """Get detailed complaint info for admin."""
    db = get_db()
    
    try:
        doc = await db.complaints.find_one({"_id": ObjectId(complaint_id)})
    except:
        raise HTTPException(status_code=400, detail="Invalid complaint ID")
    
    if not doc:
        raise HTTPException(status_code=404, detail="Complaint not found")
    
    # Check department access
    if admin.get("role") != "super_admin":
        if doc.get("department", {}).get("id") != admin.get("department_id"):
            raise HTTPException(status_code=403, detail="Not your department's complaint")
    
    # Get history
    history = await db.complaint_history.find(
        {"complaint_id": complaint_id}
    ).sort("created_at", -1).to_list(length=50)
    
    return {
        "id": str(doc["_id"]),
        "title": doc["title"],
        "description": doc["description"],
        "category": doc["category"],
        "department": doc["department"],
        "location": doc.get("location"),
        "media_urls": doc.get("media_urls", []),
        "urgency": doc["urgency"],
        "status": doc["status"],
        "upvote_count": doc.get("upvote_count", 0),
        "upvoters_count": len(doc.get("upvoters", [])),
        "created_by": doc.get("created_by"),
        "created_at": doc["created_at"],
        "assigned_to": doc.get("assigned_to"),
        "resolution_notes": doc.get("resolution_notes"),
        "resolved_at": doc.get("resolved_at"),
        "citizen_verified": doc.get("citizen_verified"),
        "history": [
            {
                "action": h.get("action"),
                "by": h.get("by"),
                "notes": h.get("notes"),
                "created_at": h.get("created_at")
            }
            for h in history
        ]
    }


# ============ Status Management ============

@router.put("/complaints/{complaint_id}/status")
async def update_complaint_status(
    complaint_id: str,
    data: StatusUpdate,
    admin: dict = Depends(get_admin_user)
):
    """Update complaint status."""
    db = get_db()
    
    try:
        doc = await db.complaints.find_one({"_id": ObjectId(complaint_id)})
    except:
        raise HTTPException(status_code=400, detail="Invalid complaint ID")
    
    if not doc:
        raise HTTPException(status_code=404, detail="Complaint not found")
    
    # Check department access
    if admin.get("role") != "super_admin":
        if doc.get("department", {}).get("id") != admin.get("department_id"):
            raise HTTPException(status_code=403, detail="Not your department's complaint")
    
    old_status = doc["status"]
    now = datetime.now(timezone.utc)
    
    update = {
        "$set": {
            "status": data.status.value,
            "updated_at": now
        }
    }
    
    if data.status == ComplaintStatus.RESOLVED:
        update["$set"]["resolved_at"] = now
    
    await db.complaints.update_one({"_id": ObjectId(complaint_id)}, update)
    
    # Add history
    await db.complaint_history.insert_one({
        "complaint_id": complaint_id,
        "action": f"status_changed",
        "from_status": old_status,
        "to_status": data.status.value,
        "by": {"id": str(admin["_id"]), "name": admin["name"]},
        "notes": data.notes,
        "created_at": now
    })
    
    return {"message": "Status updated", "new_status": data.status.value}


@router.put("/complaints/{complaint_id}/resolve")
async def resolve_complaint(
    complaint_id: str,
    data: ResolutionData,
    admin: dict = Depends(get_admin_user)
):
    """Mark complaint as resolved with resolution notes."""
    db = get_db()
    
    try:
        doc = await db.complaints.find_one({"_id": ObjectId(complaint_id)})
    except:
        raise HTTPException(status_code=400, detail="Invalid complaint ID")
    
    if not doc:
        raise HTTPException(status_code=404, detail="Complaint not found")
    
    # Check department access
    if admin.get("role") != "super_admin":
        if doc.get("department", {}).get("id") != admin.get("department_id"):
            raise HTTPException(status_code=403, detail="Not your department's complaint")
    
    now = datetime.now(timezone.utc)
    
    await db.complaints.update_one(
        {"_id": ObjectId(complaint_id)},
        {
            "$set": {
                "status": ComplaintStatus.RESOLVED.value,
                "resolution_notes": data.resolution_notes,
                "resolved_by": data.resolved_by_name or admin["name"],
                "resolved_at": now,
                "updated_at": now
            }
        }
    )
    
    # Add history
    await db.complaint_history.insert_one({
        "complaint_id": complaint_id,
        "action": "resolved",
        "by": {"id": str(admin["_id"]), "name": admin["name"]},
        "notes": data.resolution_notes,
        "created_at": now
    })
    
    return {
        "message": "Complaint marked as resolved",
        "resolved_at": now,
        "awaiting_citizen_verification": True
    }


@router.put("/complaints/{complaint_id}/assign")
async def assign_complaint(
    complaint_id: str,
    data: AssignmentData,
    admin: dict = Depends(get_admin_user)
):
    """Assign complaint to a field worker/staff."""
    db = get_db()
    
    try:
        doc = await db.complaints.find_one({"_id": ObjectId(complaint_id)})
    except:
        raise HTTPException(status_code=400, detail="Invalid complaint ID")
    
    if not doc:
        raise HTTPException(status_code=404, detail="Complaint not found")
    
    now = datetime.now(timezone.utc)
    
    await db.complaints.update_one(
        {"_id": ObjectId(complaint_id)},
        {
            "$set": {
                "status": ComplaintStatus.ASSIGNED.value,
                "assigned_to": {
                    "name": data.assigned_to_name,
                    "phone": data.assigned_to_phone,
                    "assigned_at": now
                },
                "priority": data.priority,
                "updated_at": now
            }
        }
    )
    
    # Add history
    await db.complaint_history.insert_one({
        "complaint_id": complaint_id,
        "action": "assigned",
        "by": {"id": str(admin["_id"]), "name": admin["name"]},
        "notes": f"Assigned to {data.assigned_to_name}",
        "created_at": now
    })
    
    return {"message": f"Complaint assigned to {data.assigned_to_name}"}


@router.put("/complaints/{complaint_id}/escalate")
async def escalate_complaint(
    complaint_id: str,
    data: EscalationData,
    admin: dict = Depends(get_admin_user)
):
    """Escalate complaint to higher authority."""
    db = get_db()
    
    try:
        doc = await db.complaints.find_one({"_id": ObjectId(complaint_id)})
    except:
        raise HTTPException(status_code=400, detail="Invalid complaint ID")
    
    if not doc:
        raise HTTPException(status_code=404, detail="Complaint not found")
    
    now = datetime.now(timezone.utc)
    
    # Increment escalation level
    current_level = doc.get("escalation_level", 0)
    
    await db.complaints.update_one(
        {"_id": ObjectId(complaint_id)},
        {
            "$set": {
                "escalation_level": current_level + 1,
                "escalated_at": now,
                "escalation_reason": data.reason,
                "updated_at": now
            }
        }
    )
    
    # Add history
    await db.complaint_history.insert_one({
        "complaint_id": complaint_id,
        "action": "escalated",
        "by": {"id": str(admin["_id"]), "name": admin["name"]},
        "notes": data.reason,
        "created_at": now
    })
    
    return {
        "message": "Complaint escalated",
        "new_level": current_level + 1
    }


@router.put("/complaints/{complaint_id}/reject")
async def reject_complaint(
    complaint_id: str,
    reason: str = Query(..., min_length=10),
    admin: dict = Depends(get_admin_user)
):
    """Reject a complaint with reason."""
    db = get_db()
    
    try:
        doc = await db.complaints.find_one({"_id": ObjectId(complaint_id)})
    except:
        raise HTTPException(status_code=400, detail="Invalid complaint ID")
    
    if not doc:
        raise HTTPException(status_code=404, detail="Complaint not found")
    
    now = datetime.now(timezone.utc)
    
    await db.complaints.update_one(
        {"_id": ObjectId(complaint_id)},
        {
            "$set": {
                "status": ComplaintStatus.REJECTED.value,
                "rejection_reason": reason,
                "rejected_by": {"id": str(admin["_id"]), "name": admin["name"]},
                "rejected_at": now,
                "updated_at": now
            }
        }
    )
    
    # Add history
    await db.complaint_history.insert_one({
        "complaint_id": complaint_id,
        "action": "rejected",
        "by": {"id": str(admin["_id"]), "name": admin["name"]},
        "notes": reason,
        "created_at": now
    })
    
    return {"message": "Complaint rejected", "reason": reason}


# ============ Dashboard Stats ============

@router.get("/dashboard")
async def get_dashboard_stats(
    admin: dict = Depends(get_admin_user)
):
    """Get department dashboard statistics."""
    db = get_db()
    
    # Build query based on department
    query = {}
    if admin.get("role") != "super_admin" and admin.get("department_id"):
        query["department.id"] = admin["department_id"]
    
    now = datetime.now(timezone.utc)
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    week_ago = now - timedelta(days=7)
    month_ago = now - timedelta(days=30)
    
    # Total complaints
    total = await db.complaints.count_documents(query)
    
    # By status
    pending = await db.complaints.count_documents({**query, "status": "pending"})
    assigned = await db.complaints.count_documents({**query, "status": "assigned"})
    in_progress = await db.complaints.count_documents({**query, "status": "in_progress"})
    resolved = await db.complaints.count_documents({**query, "status": "resolved"})
    rejected = await db.complaints.count_documents({**query, "status": "rejected"})
    citizen_rejected = await db.complaints.count_documents({**query, "status": "citizen_rejected"})
    
    # Today's new complaints
    today_new = await db.complaints.count_documents({
        **query,
        "created_at": {"$gte": today_start}
    })
    
    # This week's complaints
    week_new = await db.complaints.count_documents({
        **query,
        "created_at": {"$gte": week_ago}
    })
    
    # Resolved this week
    week_resolved = await db.complaints.count_documents({
        **query,
        "resolved_at": {"$gte": week_ago}
    })
    
    # High urgency pending
    high_urgency = await db.complaints.count_documents({
        **query,
        "urgency": {"$in": ["high", "critical"]},
        "status": {"$in": ["pending", "assigned", "in_progress"]}
    })
    
    # Citizen verification stats
    verified_positive = await db.complaints.count_documents({
        **query,
        "citizen_verified": True
    })
    verified_negative = await db.complaints.count_documents({
        **query,
        "citizen_verified": False
    })
    
    # Average resolution time (last 30 days)
    resolution_pipeline = [
        {"$match": {
            **query,
            "resolved_at": {"$gte": month_ago},
            "created_at": {"$exists": True}
        }},
        {"$project": {
            "resolution_time": {
                "$subtract": ["$resolved_at", "$created_at"]
            }
        }},
        {"$group": {
            "_id": None,
            "avg_time_ms": {"$avg": "$resolution_time"}
        }}
    ]
    resolution_result = await db.complaints.aggregate(resolution_pipeline).to_list(1)
    avg_resolution_hours = 0
    if resolution_result and resolution_result[0].get("avg_time_ms"):
        avg_resolution_hours = round(resolution_result[0]["avg_time_ms"] / (1000 * 60 * 60), 1)
    
    # Top categories this month
    category_pipeline = [
        {"$match": {**query, "created_at": {"$gte": month_ago}}},
        {"$group": {"_id": "$category.name", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}},
        {"$limit": 5}
    ]
    top_categories = await db.complaints.aggregate(category_pipeline).to_list(5)
    
    # Calculate scores
    resolution_rate = round((resolved / total * 100) if total > 0 else 0, 1)
    satisfaction_rate = round(
        (verified_positive / (verified_positive + verified_negative) * 100)
        if (verified_positive + verified_negative) > 0 else 0, 1
    )
    
    return {
        "department_id": admin.get("department_id"),
        "summary": {
            "total_complaints": total,
            "today_new": today_new,
            "week_new": week_new,
            "week_resolved": week_resolved,
            "high_urgency_pending": high_urgency
        },
        "by_status": {
            "pending": pending,
            "assigned": assigned,
            "in_progress": in_progress,
            "resolved": resolved,
            "rejected": rejected,
            "citizen_rejected": citizen_rejected
        },
        "performance": {
            "resolution_rate": resolution_rate,
            "satisfaction_rate": satisfaction_rate,
            "avg_resolution_hours": avg_resolution_hours,
            "verified_positive": verified_positive,
            "verified_negative": verified_negative
        },
        "top_categories": [
            {"category": c["_id"], "count": c["count"]}
            for c in top_categories
        ]
    }


@router.get("/dashboard/trends")
async def get_dashboard_trends(
    days: int = Query(30, ge=7, le=90),
    admin: dict = Depends(get_admin_user)
):
    """Get complaint trends over time for charts."""
    db = get_db()
    
    query = {}
    if admin.get("role") != "super_admin" and admin.get("department_id"):
        query["department.id"] = admin["department_id"]
    
    now = datetime.now(timezone.utc)
    start_date = now - timedelta(days=days)
    
    # Daily complaint counts
    pipeline = [
        {"$match": {**query, "created_at": {"$gte": start_date}}},
        {"$group": {
            "_id": {
                "$dateToString": {"format": "%Y-%m-%d", "date": "$created_at"}
            },
            "count": {"$sum": 1}
        }},
        {"$sort": {"_id": 1}}
    ]
    daily_data = await db.complaints.aggregate(pipeline).to_list(days)
    
    # Daily resolutions
    resolution_pipeline = [
        {"$match": {**query, "resolved_at": {"$gte": start_date}}},
        {"$group": {
            "_id": {
                "$dateToString": {"format": "%Y-%m-%d", "date": "$resolved_at"}
            },
            "count": {"$sum": 1}
        }},
        {"$sort": {"_id": 1}}
    ]
    resolution_data = await db.complaints.aggregate(resolution_pipeline).to_list(days)
    
    return {
        "period_days": days,
        "new_complaints": [{"date": d["_id"], "count": d["count"]} for d in daily_data],
        "resolutions": [{"date": d["_id"], "count": d["count"]} for d in resolution_data]
    }


# ============ Bulk Operations ============

@router.post("/complaints/bulk-assign")
async def bulk_assign(
    complaint_ids: List[str],
    data: AssignmentData,
    admin: dict = Depends(get_admin_user)
):
    """Assign multiple complaints at once."""
    db = get_db()
    now = datetime.now(timezone.utc)
    
    object_ids = []
    for cid in complaint_ids:
        try:
            object_ids.append(ObjectId(cid))
        except:
            pass
    
    result = await db.complaints.update_many(
        {"_id": {"$in": object_ids}},
        {
            "$set": {
                "status": ComplaintStatus.ASSIGNED.value,
                "assigned_to": {
                    "name": data.assigned_to_name,
                    "phone": data.assigned_to_phone,
                    "assigned_at": now
                },
                "updated_at": now
            }
        }
    )
    
    return {"message": f"Assigned {result.modified_count} complaints"}


@router.post("/complaints/bulk-status")
async def bulk_status_update(
    complaint_ids: List[str],
    new_status: ComplaintStatus,
    admin: dict = Depends(get_admin_user)
):
    """Update status of multiple complaints."""
    db = get_db()
    now = datetime.now(timezone.utc)
    
    object_ids = []
    for cid in complaint_ids:
        try:
            object_ids.append(ObjectId(cid))
        except:
            pass
    
    update = {"$set": {"status": new_status.value, "updated_at": now}}
    if new_status == ComplaintStatus.RESOLVED:
        update["$set"]["resolved_at"] = now
    
    result = await db.complaints.update_many(
        {"_id": {"$in": object_ids}},
        update
    )
    
    return {"message": f"Updated {result.modified_count} complaints"}
