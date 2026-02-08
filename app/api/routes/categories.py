from typing import List, Optional
from fastapi import APIRouter, HTTPException, status

from ..core.database import get_db

router = APIRouter(tags=["Reference Data"])


@router.get("/categories")
async def list_categories():
    """Get all complaint categories from database."""
    db = get_db()
    categories = await db.categories.find({}).to_list(length=200)
    return [
        {
            "id": str(cat["_id"]),
            "name": cat["name"],
            "description": cat.get("description", ""),
            "icon": cat.get("icon", "clipboard"),
            "default_department_id": str(cat["default_department_id"]) if cat.get("default_department_id") else None
        }
        for cat in categories
    ]


@router.get("/departments")
async def list_departments():
    """Get all departments from database."""
    db = get_db()
    departments = await db.departments.find({}).to_list(length=100)
    
    result = []
    for dept in departments:
        dept_id = str(dept["_id"])
        
        # Get categories for this department
        cats = await db.categories.find({"default_department_id": dept["_id"]}).to_list(length=50)
        category_names = [cat["name"] for cat in cats]
        
        result.append({
            "id": dept_id,
            "name": dept.get("full_name", dept.get("name", "Unknown")),
            "short_name": dept.get("name", dept.get("short_name", "?")),
            "description": dept.get("description", ""),
            "categories": category_names,
            "contact_email": dept.get("contact", {}).get("email"),
            "website": dept.get("website")
        })
    
    return result


@router.get("/departments/{dept_id}")
async def get_department(dept_id: str):
    """Get department by ID from database."""
    from bson import ObjectId
    
    db = get_db()
    
    try:
        dept = await db.departments.find_one({"_id": ObjectId(dept_id)})
    except:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid department ID")
    
    if not dept:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Department not found")
    
    # Get categories for this department
    cats = await db.categories.find({"default_department_id": dept["_id"]}).to_list(length=50)
    category_names = [cat["name"] for cat in cats]
    
    return {
        "id": str(dept["_id"]),
        "name": dept.get("full_name", dept.get("name", "Unknown")),
        "short_name": dept.get("name", dept.get("short_name", "?")),
        "description": dept.get("description", ""),
        "categories": category_names,
        "contact_email": dept.get("contact", {}).get("email"),
        "website": dept.get("website")
    }
