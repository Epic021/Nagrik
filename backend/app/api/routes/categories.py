from typing import List
from fastapi import APIRouter

from ..models.departments import (
    DELHI_DEPARTMENTS, COMPLAINT_CATEGORIES,
    DepartmentResponse, Category
)

router = APIRouter(tags=["Reference Data"])


@router.get("/categories", response_model=List[Category])
async def list_categories():
    """Get all complaint categories."""
    return COMPLAINT_CATEGORIES


@router.get("/departments", response_model=List[DepartmentResponse])
async def list_departments():
    """Get all departments."""
    result = []
    for dept in DELHI_DEPARTMENTS:
        # Map category IDs to names
        category_names = []
        for cat_id in dept.category_ids:
            for cat in COMPLAINT_CATEGORIES:
                if cat.id == cat_id:
                    category_names.append(cat.name)
                    break
        
        result.append(DepartmentResponse(
            id=dept.id,
            name=dept.name,
            short_name=dept.short_name,
            description=dept.description,
            categories=category_names,
            contact_email=dept.contact_email,
            website=dept.website
        ))
    
    return result


@router.get("/departments/{dept_id}", response_model=DepartmentResponse)
async def get_department(dept_id: str):
    """Get department by ID."""
    from fastapi import HTTPException, status
    
    for dept in DELHI_DEPARTMENTS:
        if dept.id == dept_id:
            category_names = []
            for cat_id in dept.category_ids:
                for cat in COMPLAINT_CATEGORIES:
                    if cat.id == cat_id:
                        category_names.append(cat.name)
                        break
            
            return DepartmentResponse(
                id=dept.id,
                name=dept.name,
                short_name=dept.short_name,
                description=dept.description,
                categories=category_names,
                contact_email=dept.contact_email,
                website=dept.website
            )
    
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Department not found")
