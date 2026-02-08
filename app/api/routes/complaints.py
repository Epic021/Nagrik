from typing import Optional
from fastapi import APIRouter, HTTPException, Depends, Query, status
from bson import ObjectId
from bson.errors import InvalidId

from ..models.complaints import (
    ComplaintCreate, ComplaintResponse, ComplaintListResponse, VerifyResolutionRequest
)
from ..services import complaints as complaint_service
from .auth import get_current_user

router = APIRouter(prefix="/complaints", tags=["Complaints"])


def validate_object_id(complaint_id: str) -> str:
    """Validate that complaint_id is a valid MongoDB ObjectId."""
    try:
        ObjectId(complaint_id)
        return complaint_id
    except InvalidId:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid complaint ID format: {complaint_id}"
        )


@router.post("", response_model=ComplaintResponse, status_code=status.HTTP_201_CREATED)
async def create_complaint(
    complaint_data: ComplaintCreate,
    user: dict = Depends(get_current_user)
):
    """
    Submit a new complaint.
    
    If a similar complaint exists nearby (same category, within 200m, similar text),
    it will be merged by upvoting the existing one instead of creating a duplicate.
    """
    try:
        complaint, is_new, duplicate_id = await complaint_service.create_complaint(
            complaint_data=complaint_data,
            user_id=str(user["_id"]),
            user_name=user["name"]
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    
    # Add header to indicate if merged
    if not is_new:
        complaint.merged_into = duplicate_id
    
    return complaint


@router.get("", response_model=ComplaintListResponse)
async def list_complaints(
    category: Optional[str] = Query(None, description="Filter by category ID"),
    department: Optional[str] = Query(None, description="Filter by department ID"),
    status: Optional[str] = Query(None, description="Filter by status"),
    lat: Optional[float] = Query(None, description="Latitude for nearby search"),
    lng: Optional[float] = Query(None, description="Longitude for nearby search"),
    radius: float = Query(10, description="Search radius in km"),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    sort: str = Query("created_at", description="Sort by: created_at, upvotes, urgency"),
    user: dict = Depends(get_current_user)
):
    """List complaints with optional filters."""
    complaints, total = await complaint_service.list_complaints(
        category_id=category,
        department_id=department,
        status=status,
        lat=lat,
        lng=lng,
        radius_km=radius,
        page=page,
        limit=limit,
        sort_by=sort,
        user_id=str(user["_id"])
    )
    
    return ComplaintListResponse(
        complaints=complaints,
        total=total,
        page=page,
        limit=limit,
        has_more=(page * limit) < total
    )


@router.get("/my", response_model=ComplaintListResponse)
async def get_my_complaints(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    user: dict = Depends(get_current_user)
):
    """Get complaints submitted by the current user."""
    complaints, total = await complaint_service.get_user_complaints(
        user_id=str(user["_id"]),
        page=page,
        limit=limit
    )
    
    return ComplaintListResponse(
        complaints=complaints,
        total=total,
        page=page,
        limit=limit,
        has_more=(page * limit) < total
    )


@router.get("/nearby", response_model=ComplaintListResponse)
async def get_nearby_complaints(
    lat: float = Query(..., description="Latitude"),
    lng: float = Query(..., description="Longitude"),
    radius: float = Query(5, description="Radius in km"),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    user: dict = Depends(get_current_user)
):
    """Get complaints near a location."""
    complaints, total = await complaint_service.list_complaints(
        lat=lat,
        lng=lng,
        radius_km=radius,
        page=page,
        limit=limit,
        sort_by="upvotes",
        user_id=str(user["_id"])
    )
    
    return ComplaintListResponse(
        complaints=complaints,
        total=total,
        page=page,
        limit=limit,
        has_more=(page * limit) < total
    )


@router.get("/{complaint_id}", response_model=ComplaintResponse)
async def get_complaint(complaint_id: str, user: dict = Depends(get_current_user)):
    """Get complaint by ID."""
    validate_object_id(complaint_id)
    complaint = await complaint_service.get_complaint_by_id(complaint_id, str(user["_id"]))
    if not complaint:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Complaint not found")
    return complaint


@router.post("/{complaint_id}/upvote", status_code=status.HTTP_200_OK)
async def upvote_complaint(complaint_id: str, user: dict = Depends(get_current_user)):
    """Upvote a complaint."""
    validate_object_id(complaint_id)
    success = await complaint_service.upvote_complaint(complaint_id, str(user["_id"]))
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Already upvoted or complaint not found"
        )
    return {"message": "Upvoted successfully"}


@router.delete("/{complaint_id}/upvote", status_code=status.HTTP_200_OK)
async def remove_upvote(complaint_id: str, user: dict = Depends(get_current_user)):
    """Remove upvote from a complaint."""
    validate_object_id(complaint_id)
    success = await complaint_service.remove_upvote(complaint_id, str(user["_id"]))
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Not upvoted or complaint not found"
        )
    return {"message": "Upvote removed"}


@router.post("/{complaint_id}/verify", status_code=status.HTTP_200_OK)
async def verify_resolution(
    complaint_id: str,
    request: VerifyResolutionRequest,
    user: dict = Depends(get_current_user)
):
    """
    Citizen verifies if the resolution is satisfactory.
    Only the complaint creator can verify.
    If rejected, department's leaderboard score is penalized.
    """
    validate_object_id(complaint_id)
    success = await complaint_service.verify_resolution(
        complaint_id=complaint_id,
        user_id=str(user["_id"]),
        accepted=request.accepted,
        feedback=request.feedback
    )
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot verify - not your complaint or not resolved"
        )
    
    return {"message": "Verification recorded", "accepted": request.accepted}
