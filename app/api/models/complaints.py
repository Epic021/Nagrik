from datetime import datetime
from enum import Enum
from typing import Optional, List
from pydantic import BaseModel, Field


class ComplaintStatus(str, Enum):
    PENDING = "pending"
    ASSIGNED = "assigned"
    IN_PROGRESS = "in_progress"
    RESOLVED = "resolved"
    REJECTED = "rejected"
    CITIZEN_REJECTED = "citizen_rejected"  # Citizen rejected the resolution


class Urgency(str, Enum):
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"


class GeoLocation(BaseModel):
    """MongoDB GeoJSON format for 2dsphere queries."""
    type: str = "Point"
    coordinates: List[float]  # [longitude, latitude]


class Location(BaseModel):
    lat: float = Field(..., ge=-90, le=90)
    lng: float = Field(..., ge=-180, le=180)
    address: Optional[str] = None
    
    def to_geojson(self) -> GeoLocation:
        """Convert to MongoDB GeoJSON format."""
        return GeoLocation(coordinates=[self.lng, self.lat])


class CategoryRef(BaseModel):
    id: str
    name: str


class DepartmentRef(BaseModel):
    id: str
    name: str
    short_name: Optional[str] = None


class UserRef(BaseModel):
    id: str
    name: str


# === Create Complaint ===
class ComplaintCreate(BaseModel):
    title: str = Field(..., min_length=5, max_length=200)
    description: str = Field(..., min_length=10, max_length=2000)
    category_id: str
    location: Location
    media_urls: List[str] = Field(default_factory=list, max_length=5)
    urgency: Urgency = Urgency.NORMAL


# === Knowledge Graph / AI Integration ===
class AIMetadata(BaseModel):
    """Metadata from AI/ML services for Knowledge Graph integration."""
    # Entity linking for Knowledge Graph
    kg_entity_id: Optional[str] = None  # Unique ID in knowledge graph
    
    # Related entities (for graph connections)
    related_complaint_ids: List[str] = Field(default_factory=list)  # Similar/related complaints
    hotspot_id: Optional[str] = None  # Linked hotspot cluster ID
    
    # Context Engine outputs
    extracted_entities: List[str] = Field(default_factory=list)  # Extracted keywords/entities
    sentiment_score: Optional[float] = None  # -1 to 1
    
    # Similarity Engine outputs  
    text_embedding_id: Optional[str] = None  # Vector embedding reference
    similarity_cluster_id: Optional[str] = None  # Dedup cluster ID
    
    # RAG Engine outputs
    suggested_department_id: Optional[str] = None  # AI-suggested department
    suggested_urgency: Optional[str] = None  # AI-suggested urgency
    confidence_score: Optional[float] = None  # AI confidence (0-1)
    
    # Prediction/Escalation (future)
    predicted_resolution_hours: Optional[float] = None
    escalation_risk_score: Optional[float] = None  # 0-1, high means likely to escalate


# === Complaint in DB ===
class ComplaintInDB(BaseModel):
    id: str
    title: str
    description: str
    category: CategoryRef
    department: DepartmentRef
    location: Location
    geo_location: GeoLocation  # For MongoDB geo queries
    media_urls: List[str]
    urgency: Urgency
    status: ComplaintStatus
    upvote_count: int
    upvoters: List[str]  # User IDs who upvoted
    duplicate_of: Optional[str] = None  # If merged into another complaint
    created_by: UserRef
    created_at: datetime
    updated_at: datetime
    resolved_at: Optional[datetime] = None
    resolution_notes: Optional[str] = None
    citizen_verified: Optional[bool] = None  # True if citizen confirmed fix
    
    # AI/ML Integration
    ai_metadata: Optional[AIMetadata] = None


# === Response models ===
class ComplaintResponse(BaseModel):
    id: str
    title: str
    description: str
    category: CategoryRef
    department: DepartmentRef
    location: Location
    media_urls: List[str]
    urgency: Urgency
    status: ComplaintStatus
    upvote_count: int
    has_upvoted: bool = False  # Whether current user has upvoted
    created_by: UserRef
    created_at: datetime
    resolved_at: Optional[datetime] = None
    citizen_verified: Optional[bool] = None
    
    # AI/ML Integration (optional, populated by AI services)
    related_complaints: Optional[List[str]] = None  # IDs of related complaints from KG
    ai_suggested_urgency: Optional[str] = None
    ai_confidence: Optional[float] = None


class ComplaintListResponse(BaseModel):
    complaints: List[ComplaintResponse]
    total: int
    page: int
    limit: int
    has_more: bool


class VerifyResolutionRequest(BaseModel):
    accepted: bool
    feedback: Optional[str] = None
