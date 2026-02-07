"""
AI/ML Service Interface

This module defines the interface for AI/ML services integration.
The actual implementation will be done by the AI/ML team.

Services:
- RAG Engine: Intelligent complaint understanding and routing
- Context Engine: Entity extraction and contextual reasoning
- Similarity Engine: Complaint deduplication and clustering
- Location Validator: Geographic validation via Google Maps
- Knowledge Graph: Entity linking and relationship management
"""

from abc import ABC, abstractmethod
from typing import Optional, List, Dict, Any
from pydantic import BaseModel


# === Data Transfer Objects ===

class ComplaintAnalysisRequest(BaseModel):
    """Request to AI services for complaint analysis."""
    complaint_id: str
    title: str
    description: str
    category_id: str
    location: Dict[str, float]  # {lat, lng}
    media_urls: List[str]
    

class ComplaintAnalysisResponse(BaseModel):
    """Response from AI services."""
    # RAG Engine outputs
    suggested_department_id: Optional[str] = None
    suggested_urgency: Optional[str] = None  # low, medium, high
    confidence_score: float = 0.0
    
    # Context Engine outputs
    extracted_entities: List[str] = []
    sentiment_score: Optional[float] = None
    
    # Similarity Engine outputs
    duplicate_complaint_id: Optional[str] = None  # If duplicate found
    similar_complaint_ids: List[str] = []
    similarity_cluster_id: Optional[str] = None
    
    # Knowledge Graph outputs
    kg_entity_id: Optional[str] = None
    hotspot_id: Optional[str] = None


class LocationValidationRequest(BaseModel):
    """Request to validate and enrich location data."""
    lat: float
    lng: float
    address: Optional[str] = None


class LocationValidationResponse(BaseModel):
    """Response from location validator."""
    is_valid: bool
    normalized_address: Optional[str] = None
    locality: Optional[str] = None
    district: Optional[str] = None
    pincode: Optional[str] = None
    ward: Optional[str] = None  # Municipal ward


class KnowledgeGraphQuery(BaseModel):
    """Query for knowledge graph."""
    entity_type: str  # complaint, location, department, user
    entity_id: str
    relationship_type: Optional[str] = None  # e.g., "similar_to", "located_at", "assigned_to"
    depth: int = 1  # Traversal depth


class KnowledgeGraphResult(BaseModel):
    """Result from knowledge graph query."""
    nodes: List[Dict[str, Any]]
    edges: List[Dict[str, Any]]


# === Service Interfaces ===

class RAGEngineInterface(ABC):
    """
    RAG Engine interface for intelligent complaint processing.
    
    Responsibilities:
    - Understand complaint context from text + images
    - Suggest appropriate department
    - Suggest urgency level
    - Answer queries about complaints (future: chat interface)
    """
    
    @abstractmethod
    async def analyze_complaint(
        self, request: ComplaintAnalysisRequest
    ) -> ComplaintAnalysisResponse:
        """Analyze a complaint and provide routing suggestions."""
        pass
    
    @abstractmethod
    async def get_similar_resolutions(
        self, complaint_id: str, limit: int = 5
    ) -> List[Dict[str, Any]]:
        """Get similar past complaints and their resolutions."""
        pass


class ContextEngineInterface(ABC):
    """
    Context Engine interface for entity extraction and reasoning.
    
    Responsibilities:
    - Extract entities (landmarks, locations, issues) from text
    - Understand complaint context
    - Detect sentiment
    """
    
    @abstractmethod
    async def extract_entities(
        self, text: str, media_urls: List[str] = None
    ) -> Dict[str, Any]:
        """Extract entities and context from complaint."""
        pass
    
    @abstractmethod
    async def get_sentiment(self, text: str) -> float:
        """Get sentiment score (-1 to 1)."""
        pass


class SimilarityEngineInterface(ABC):
    """
    Similarity Engine interface for deduplication.
    
    Responsibilities:
    - Detect duplicate complaints
    - Cluster similar complaints
    - Manage text embeddings
    """
    
    @abstractmethod
    async def find_duplicates(
        self,
        title: str,
        description: str,
        category_id: str,
        lat: float,
        lng: float,
        radius_meters: int = 200
    ) -> Optional[str]:
        """Find duplicate complaint ID, or None if no duplicate."""
        pass
    
    @abstractmethod
    async def get_similar_complaints(
        self, complaint_id: str, limit: int = 10
    ) -> List[str]:
        """Get IDs of similar complaints."""
        pass
    
    @abstractmethod
    async def create_embedding(
        self, complaint_id: str, text: str
    ) -> str:
        """Create and store text embedding, return embedding ID."""
        pass


class LocationValidatorInterface(ABC):
    """
    Location Validator interface using Google Maps.
    
    Responsibilities:
    - Validate coordinates are within serviceable area
    - Reverse geocode to get address
    - Get locality/ward info for routing
    """
    
    @abstractmethod
    async def validate_location(
        self, request: LocationValidationRequest
    ) -> LocationValidationResponse:
        """Validate and enrich location data."""
        pass
    
    @abstractmethod
    async def geocode_address(self, address: str) -> Optional[Dict[str, float]]:
        """Convert address to coordinates. Returns {lat, lng}."""
        pass


class KnowledgeGraphInterface(ABC):
    """
    Knowledge Graph interface for entity linking.
    
    Responsibilities:
    - Link complaints to locations, departments, users
    - Track resolution history
    - Detect recurring issue hotspots
    - Support graph queries for insights
    """
    
    @abstractmethod
    async def add_complaint_node(
        self, complaint_id: str, data: Dict[str, Any]
    ) -> str:
        """Add complaint to knowledge graph, return KG entity ID."""
        pass
    
    @abstractmethod
    async def link_entities(
        self, from_id: str, to_id: str, relationship: str
    ) -> bool:
        """Create relationship between entities."""
        pass
    
    @abstractmethod
    async def query(self, query: KnowledgeGraphQuery) -> KnowledgeGraphResult:
        """Query the knowledge graph."""
        pass
    
    @abstractmethod
    async def get_hotspots(
        self, lat: float, lng: float, radius_km: float = 5
    ) -> List[Dict[str, Any]]:
        """Get complaint hotspots near a location."""
        pass


# === Stub Implementations (for development without AI services) ===

class StubRAGEngine(RAGEngineInterface):
    """Stub implementation that passes through without AI processing."""
    
    async def analyze_complaint(
        self, request: ComplaintAnalysisRequest
    ) -> ComplaintAnalysisResponse:
        return ComplaintAnalysisResponse(confidence_score=0.0)
    
    async def get_similar_resolutions(
        self, complaint_id: str, limit: int = 5
    ) -> List[Dict[str, Any]]:
        return []


class StubContextEngine(ContextEngineInterface):
    """Stub implementation."""
    
    async def extract_entities(
        self, text: str, media_urls: List[str] = None
    ) -> Dict[str, Any]:
        return {"entities": []}
    
    async def get_sentiment(self, text: str) -> float:
        return 0.0


class StubSimilarityEngine(SimilarityEngineInterface):
    """Stub that uses basic text matching (current implementation)."""
    
    async def find_duplicates(
        self,
        title: str,
        description: str,
        category_id: str,
        lat: float,
        lng: float,
        radius_meters: int = 200
    ) -> Optional[str]:
        # Defer to existing deduplication service
        from .deduplication import find_duplicate_complaint
        return await find_duplicate_complaint(
            category_id=category_id,
            lat=lat,
            lng=lng,
            title=title,
            description=description
        )
    
    async def get_similar_complaints(
        self, complaint_id: str, limit: int = 10
    ) -> List[str]:
        return []
    
    async def create_embedding(
        self, complaint_id: str, text: str
    ) -> str:
        return ""


class StubLocationValidator(LocationValidatorInterface):
    """Stub that does basic validation."""
    
    async def validate_location(
        self, request: LocationValidationRequest
    ) -> LocationValidationResponse:
        # Basic validation: check if in Delhi NCR region
        delhi_bounds = {
            "min_lat": 28.40,
            "max_lat": 28.88,
            "min_lng": 76.84,
            "max_lng": 77.35
        }
        is_valid = (
            delhi_bounds["min_lat"] <= request.lat <= delhi_bounds["max_lat"] and
            delhi_bounds["min_lng"] <= request.lng <= delhi_bounds["max_lng"]
        )
        return LocationValidationResponse(
            is_valid=is_valid,
            normalized_address=request.address
        )
    
    async def geocode_address(self, address: str) -> Optional[Dict[str, float]]:
        return None


class StubKnowledgeGraph(KnowledgeGraphInterface):
    """Stub implementation."""
    
    async def add_complaint_node(
        self, complaint_id: str, data: Dict[str, Any]
    ) -> str:
        return complaint_id
    
    async def link_entities(
        self, from_id: str, to_id: str, relationship: str
    ) -> bool:
        return True
    
    async def query(self, query: KnowledgeGraphQuery) -> KnowledgeGraphResult:
        return KnowledgeGraphResult(nodes=[], edges=[])
    
    async def get_hotspots(
        self, lat: float, lng: float, radius_km: float = 5
    ) -> List[Dict[str, Any]]:
        return []


# === Service Registry ===

class AIServiceRegistry:
    """
    Registry for AI/ML services.
    
    Use this to get service instances. In production, replace stubs
    with real implementations.
    """
    
    _rag_engine: RAGEngineInterface = None
    _context_engine: ContextEngineInterface = None
    _similarity_engine: SimilarityEngineInterface = None
    _location_validator: LocationValidatorInterface = None
    _knowledge_graph: KnowledgeGraphInterface = None
    
    @classmethod
    def get_rag_engine(cls) -> RAGEngineInterface:
        if cls._rag_engine is None:
            cls._rag_engine = StubRAGEngine()
        return cls._rag_engine
    
    @classmethod
    def get_context_engine(cls) -> ContextEngineInterface:
        if cls._context_engine is None:
            cls._context_engine = StubContextEngine()
        return cls._context_engine
    
    @classmethod
    def get_similarity_engine(cls) -> SimilarityEngineInterface:
        if cls._similarity_engine is None:
            cls._similarity_engine = StubSimilarityEngine()
        return cls._similarity_engine
    
    @classmethod
    def get_location_validator(cls) -> LocationValidatorInterface:
        if cls._location_validator is None:
            cls._location_validator = StubLocationValidator()
        return cls._location_validator
    
    @classmethod
    def get_knowledge_graph(cls) -> KnowledgeGraphInterface:
        if cls._knowledge_graph is None:
            cls._knowledge_graph = StubKnowledgeGraph()
        return cls._knowledge_graph
    
    @classmethod
    def register_rag_engine(cls, engine: RAGEngineInterface):
        cls._rag_engine = engine
    
    @classmethod
    def register_context_engine(cls, engine: ContextEngineInterface):
        cls._context_engine = engine
    
    @classmethod
    def register_similarity_engine(cls, engine: SimilarityEngineInterface):
        cls._similarity_engine = engine
    
    @classmethod
    def register_location_validator(cls, validator: LocationValidatorInterface):
        cls._location_validator = validator
    
    @classmethod
    def register_knowledge_graph(cls, kg: KnowledgeGraphInterface):
        cls._knowledge_graph = kg
