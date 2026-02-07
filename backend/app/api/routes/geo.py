"""
Geocoding routes - Address to coordinates conversion using Google Maps API
"""
from typing import Optional
from fastapi import APIRouter, HTTPException, Query, status

from ..services.google_services import (
    geocode_address,
    reverse_geocode,
    validate_delhi_location
)

router = APIRouter(prefix="/geo", tags=["Geocoding"])


@router.get("/geocode")
async def geocode(address: str = Query(..., description="Address to geocode")):
    """
    Convert an address to lat/lng coordinates using Google Maps Geocoding API.
    """
    result = await geocode_address(address)
    
    if not result:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Could not geocode the address. Check if Google Maps API key is configured."
        )
    
    # Check if within Delhi
    is_delhi = validate_delhi_location(result["lat"], result["lng"])
    
    return {
        "lat": result["lat"],
        "lng": result["lng"],
        "is_valid_delhi_location": is_delhi
    }


@router.get("/reverse")
async def reverse_geocode_endpoint(
    lat: float = Query(..., description="Latitude"),
    lng: float = Query(..., description="Longitude")
):
    """
    Convert coordinates to address using Google Maps Reverse Geocoding API.
    """
    result = await reverse_geocode(lat, lng)
    
    if not result:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Could not reverse geocode. Check if Google Maps API key is configured."
        )
    
    is_delhi = validate_delhi_location(lat, lng)
    
    return {
        "lat": lat,
        "lng": lng,
        "is_valid_delhi_location": is_delhi,
        "address": result.get("formatted_address", ""),
        "locality": result.get("locality", ""),
        "sublocality": result.get("sublocality", ""),
        "district": result.get("district", ""),
        "pincode": result.get("pincode", "")
    }


@router.get("/validate")
async def validate_location(
    lat: float = Query(..., description="Latitude"),
    lng: float = Query(..., description="Longitude")
):
    """
    Validate if a location is within Delhi NCR boundaries.
    """
    is_valid = validate_delhi_location(lat, lng)
    
    return {
        "lat": lat,
        "lng": lng,
        "is_valid_delhi_location": is_valid,
        "message": "Location is within Delhi NCR" if is_valid else "Location is outside Delhi NCR"
    }
