"""
Google Cloud Services Integration

Real implementations for:
- Google Cloud Storage (file uploads)
- Google Maps Geocoding API
"""
import httpx
from typing import Optional, Dict
from google.cloud import storage
from google.oauth2 import service_account

from ..core.config import get_settings

settings = get_settings()

_gcs_client: storage.Client | None = None
_gcs_bucket: storage.Bucket | None = None


def get_gcs_client() -> Optional[storage.Client]:
    """Get Google Cloud Storage client."""
    global _gcs_client
    
    if _gcs_client is not None:
        return _gcs_client
    
    if not settings.GCS_SERVICE_ACCOUNT_KEY:
        print("[WARN] GCS_SERVICE_ACCOUNT_KEY not set")
        return None
    
    try:
        credentials = service_account.Credentials.from_service_account_file(
            settings.GCS_SERVICE_ACCOUNT_KEY
        )
        _gcs_client = storage.Client(credentials=credentials)
        print(f"[OK] GCS client initialized")
        return _gcs_client
    except Exception as e:
        print(f"[WARN] Failed to init GCS client: {e}")
        return None


def get_gcs_bucket() -> Optional[storage.Bucket]:
    """Get or create GCS bucket."""
    global _gcs_bucket
    
    if _gcs_bucket is not None:
        return _gcs_bucket
    
    client = get_gcs_client()
    if not client:
        return None
    
    try:
        _gcs_bucket = client.bucket(settings.GCS_BUCKET_NAME)
        # Check if bucket exists, if not create it
        if not _gcs_bucket.exists():
            _gcs_bucket = client.create_bucket(
                settings.GCS_BUCKET_NAME,
                location="asia-south1"  # Mumbai region
            )
            # Make bucket publicly readable for complaint images
            _gcs_bucket.make_public(recursive=True, future=True)
            print(f"[OK] Created GCS bucket: {settings.GCS_BUCKET_NAME}")
        else:
            print(f"[OK] Using GCS bucket: {settings.GCS_BUCKET_NAME}")
        return _gcs_bucket
    except Exception as e:
        print(f"[WARN] Failed to get/create bucket: {e}")
        return None


async def upload_to_gcs(
    file_content: bytes,
    filename: str,
    content_type: str
) -> Optional[str]:
    """
    Upload file to Google Cloud Storage.
    Returns public URL or None if failed.
    """
    bucket = get_gcs_bucket()
    if not bucket:
        return None
    
    try:
        blob = bucket.blob(filename)
        blob.upload_from_string(file_content, content_type=content_type)
        blob.make_public()
        return blob.public_url
    except Exception as e:
        print(f"GCS upload error: {e}")
        return None


async def geocode_address(address: str) -> Optional[Dict[str, float]]:
    """
    Convert address to coordinates using Google Maps Geocoding API.
    Returns {lat, lng} or None.
    """
    if not settings.GOOGLE_MAPS_API_KEY:
        print("[WARN] GOOGLE_MAPS_API_KEY not set")
        return None
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                "https://maps.googleapis.com/maps/api/geocode/json",
                params={
                    "address": address,
                    "key": settings.GOOGLE_MAPS_API_KEY,
                    "region": "in"  # Bias to India
                }
            )
            data = response.json()
            
            if data["status"] == "OK" and data["results"]:
                location = data["results"][0]["geometry"]["location"]
                return {"lat": location["lat"], "lng": location["lng"]}
            return None
    except Exception as e:
        print(f"Geocoding error: {e}")
        return None


async def reverse_geocode(lat: float, lng: float) -> Optional[Dict[str, str]]:
    """
    Convert coordinates to address using Google Maps Geocoding API.
    Returns address components or None.
    """
    if not settings.GOOGLE_MAPS_API_KEY:
        return None
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                "https://maps.googleapis.com/maps/api/geocode/json",
                params={
                    "latlng": f"{lat},{lng}",
                    "key": settings.GOOGLE_MAPS_API_KEY
                }
            )
            data = response.json()
            
            if data["status"] == "OK" and data["results"]:
                result = data["results"][0]
                components = {}
                
                for component in result.get("address_components", []):
                    types = component.get("types", [])
                    if "locality" in types:
                        components["locality"] = component["long_name"]
                    if "sublocality" in types:
                        components["sublocality"] = component["long_name"]
                    if "administrative_area_level_2" in types:
                        components["district"] = component["long_name"]
                    if "postal_code" in types:
                        components["pincode"] = component["long_name"]
                
                components["formatted_address"] = result.get("formatted_address", "")
                return components
            return None
    except Exception as e:
        print(f"Reverse geocoding error: {e}")
        return None


def validate_delhi_location(lat: float, lng: float) -> bool:
    """Check if coordinates are within Delhi NCR region."""
    delhi_bounds = {
        "min_lat": 28.40,
        "max_lat": 28.88,
        "min_lng": 76.84,
        "max_lng": 77.35
    }
    return (
        delhi_bounds["min_lat"] <= lat <= delhi_bounds["max_lat"] and
        delhi_bounds["min_lng"] <= lng <= delhi_bounds["max_lng"]
    )
