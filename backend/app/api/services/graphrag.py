"""
MS GraphRAG Integration for NAGRIK Knowledge Graph

This module provides the interface for MS GraphRAG integration.
The KG teammate should implement the actual GraphRAG client here.

GraphRAG handles:
1. Duplicate detection (semantic similarity across complaints)
2. Hotspot detection (geographic clustering)
3. Department performance analysis
4. Related complaint discovery
5. Trend prediction

=== INSTRUCTIONS FOR KG TEAMMATE ===

1. Install MS GraphRAG:
   pip install graphrag

2. Set environment variables in .env:
   GRAPHRAG_ENDPOINT=http://localhost:8080
   GRAPHRAG_API_KEY=your-key

3. Initialize your GraphRAG index with these entity types:
   - Complaint (id, title, description, category, location, status, created_at)
   - Location (lat, lng, address, locality, ward)
   - Department (id, name, contact)
   - Category (id, name)
   - Resolution (complaint_id, resolved_at, satisfaction_score)

4. Define relationships:
   - Complaint -[LOCATED_AT]-> Location
   - Complaint -[ASSIGNED_TO]-> Department
   - Complaint -[HAS_CATEGORY]-> Category
   - Complaint -[SIMILAR_TO]-> Complaint
   - Complaint -[RESOLVED_BY]-> Resolution
   - Location -[NEARBY]-> Location

5. Replace the stub methods below with actual GraphRAG calls.

6. The methods are called from:
   - complaints.py (on create) -> add_complaint, find_duplicates
   - leaderboards.py -> get_hotspots, get_department_stats
   - ai.py -> query, get_related

=====================================
"""
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
import httpx

from ..core.config import get_settings

settings = get_settings()


@dataclass
class GraphNode:
    """Represents a node in the knowledge graph."""
    id: str
    type: str  # complaint, location, department, category
    properties: Dict[str, Any]


@dataclass
class GraphEdge:
    """Represents an edge/relationship in the knowledge graph."""
    from_id: str
    to_id: str
    relationship: str  # SIMILAR_TO, LOCATED_AT, ASSIGNED_TO, etc.
    weight: float = 1.0
    properties: Dict[str, Any] = None


@dataclass
class DuplicateResult:
    """Result of duplicate detection."""
    is_duplicate: bool
    confidence: float
    original_complaint_id: Optional[str]
    similarity_score: float
    merge_recommended: bool


@dataclass
class HotspotResult:
    """Detected complaint hotspot."""
    center_lat: float
    center_lng: float
    radius_meters: float
    complaint_count: int
    dominant_category: str
    severity_score: float
    trend: str  # increasing, stable, decreasing


class GraphRAGInterface(ABC):
    """
    Abstract interface for MS GraphRAG.
    KG teammate: Implement these methods with actual GraphRAG calls.
    """
    
    @abstractmethod
    async def add_complaint(self, complaint_data: Dict[str, Any]) -> str:
        """
        Index a new complaint in GraphRAG.
        
        Args:
            complaint_data: {
                "id": str,
                "title": str,
                "description": str,
                "category_id": str,
                "department_id": str,
                "location": {"lat": float, "lng": float, "address": str},
                "urgency": str,
                "created_at": datetime
            }
        
        Returns:
            GraphRAG entity ID
        """
        pass
    
    @abstractmethod
    async def find_duplicates(
        self,
        title: str,
        description: str,
        category_id: str,
        lat: float,
        lng: float,
        radius_meters: float = 500
    ) -> List[DuplicateResult]:
        """
        Find semantically similar complaints nearby.
        
        This is where GraphRAG's semantic search shines - it can find
        "Pothole on road" as similar to "Road has big hole" even though
        they use different words.
        
        Returns list of potential duplicates, sorted by similarity.
        """
        pass
    
    @abstractmethod
    async def get_hotspots(
        self,
        lat: float,
        lng: float,
        radius_km: float = 10,
        min_complaints: int = 5,
        time_window_days: int = 30
    ) -> List[HotspotResult]:
        """
        Detect complaint hotspots using GraphRAG clustering.
        
        Hotspots are areas with unusually high complaint density.
        Use for predictive maintenance and resource allocation.
        """
        pass
    
    @abstractmethod
    async def get_department_performance(
        self,
        department_id: Optional[str] = None,
        time_window_days: int = 30
    ) -> List[Dict[str, Any]]:
        """
        Analyze department performance using graph traversal.
        
        Returns:
            [{
                "department_id": str,
                "department_name": str,
                "total_complaints": int,
                "resolved_count": int,
                "avg_resolution_hours": float,
                "citizen_satisfaction": float,  # 0-1
                "trending_categories": [str],
                "score": float  # Overall performance score
            }]
        """
        pass
    
    @abstractmethod
    async def get_related_complaints(
        self,
        complaint_id: str,
        max_results: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Find complaints related to this one via graph traversal.
        
        Relationships considered:
        - SIMILAR_TO (semantic similarity)
        - NEARBY (same location cluster)
        - SAME_CATEGORY
        - SAME_DEPARTMENT
        
        Returns list of related complaints with relationship info.
        """
        pass
    
    @abstractmethod
    async def update_complaint_status(
        self,
        complaint_id: str,
        new_status: str,
        resolution_data: Optional[Dict] = None
    ) -> bool:
        """Update complaint status in the graph."""
        pass
    
    @abstractmethod
    async def link_complaints(
        self,
        complaint_id_1: str,
        complaint_id_2: str,
        relationship: str = "SIMILAR_TO",
        confidence: float = 1.0
    ) -> bool:
        """Create a relationship between two complaints."""
        pass


class StubGraphRAG(GraphRAGInterface):
    """
    Stub implementation for development.
    Replace with actual MS GraphRAG integration.
    """
    
    def __init__(self):
        self._complaints: Dict[str, Dict] = {}
    
    async def add_complaint(self, complaint_data: Dict[str, Any]) -> str:
        entity_id = f"graphrag_{complaint_data['id']}"
        self._complaints[entity_id] = complaint_data
        print(f"[GraphRAG STUB] Added complaint: {entity_id}")
        return entity_id
    
    async def find_duplicates(
        self,
        title: str,
        description: str,
        category_id: str,
        lat: float,
        lng: float,
        radius_meters: float = 500
    ) -> List[DuplicateResult]:
        # Stub: Always return no duplicates
        # Real implementation uses GraphRAG semantic search
        print(f"[GraphRAG STUB] Checking duplicates for: {title[:30]}...")
        return []
    
    async def get_hotspots(
        self,
        lat: float,
        lng: float,
        radius_km: float = 10,
        min_complaints: int = 5,
        time_window_days: int = 30
    ) -> List[HotspotResult]:
        # Stub: Return sample hotspots
        print(f"[GraphRAG STUB] Getting hotspots around ({lat}, {lng})")
        return [
            HotspotResult(
                center_lat=lat + 0.01,
                center_lng=lng + 0.01,
                radius_meters=200,
                complaint_count=15,
                dominant_category="potholes",
                severity_score=0.7,
                trend="increasing"
            )
        ]
    
    async def get_department_performance(
        self,
        department_id: Optional[str] = None,
        time_window_days: int = 30
    ) -> List[Dict[str, Any]]:
        # Stub: Return sample performance data
        print(f"[GraphRAG STUB] Getting department performance")
        return [
            {
                "department_id": "mcd",
                "department_name": "Municipal Corporation of Delhi",
                "total_complaints": 150,
                "resolved_count": 120,
                "avg_resolution_hours": 72,
                "citizen_satisfaction": 0.75,
                "trending_categories": ["potholes", "garbage"],
                "score": 0.68
            }
        ]
    
    async def get_related_complaints(
        self,
        complaint_id: str,
        max_results: int = 10
    ) -> List[Dict[str, Any]]:
        print(f"[GraphRAG STUB] Getting related complaints for: {complaint_id}")
        return []
    
    async def update_complaint_status(
        self,
        complaint_id: str,
        new_status: str,
        resolution_data: Optional[Dict] = None
    ) -> bool:
        print(f"[GraphRAG STUB] Updated status: {complaint_id} -> {new_status}")
        return True
    
    async def link_complaints(
        self,
        complaint_id_1: str,
        complaint_id_2: str,
        relationship: str = "SIMILAR_TO",
        confidence: float = 1.0
    ) -> bool:
        print(f"[GraphRAG STUB] Linked: {complaint_id_1} -{relationship}-> {complaint_id_2}")
        return True


# === GraphRAG Client (KG Teammate implements this) ===

class MSGraphRAGClient(GraphRAGInterface):
    """
    Actual MS GraphRAG implementation.
    
    KG Teammate: Uncomment and implement this class.
    Then update get_graphrag() to return this instead of StubGraphRAG.
    """
    
    def __init__(self, endpoint: str, api_key: str):
        self.endpoint = endpoint
        self.api_key = api_key
        self.client = httpx.AsyncClient(
            base_url=endpoint,
            headers={"Authorization": f"Bearer {api_key}"}
        )
    
    async def add_complaint(self, complaint_data: Dict[str, Any]) -> str:
        # TODO: Implement actual GraphRAG indexing
        # response = await self.client.post("/index", json={
        #     "documents": [complaint_data],
        #     "entity_types": ["Complaint", "Location", "Category"]
        # })
        # return response.json()["entity_id"]
        raise NotImplementedError("KG teammate: Implement GraphRAG indexing")
    
    async def find_duplicates(
        self,
        title: str,
        description: str,
        category_id: str,
        lat: float,
        lng: float,
        radius_meters: float = 500
    ) -> List[DuplicateResult]:
        # TODO: Implement semantic search with location filter
        # response = await self.client.post("/query", json={
        #     "query": f"{title} {description}",
        #     "filters": {
        #         "category": category_id,
        #         "location": {"lat": lat, "lng": lng, "radius": radius_meters}
        #     },
        #     "top_k": 5
        # })
        raise NotImplementedError("KG teammate: Implement duplicate detection")
    
    async def get_hotspots(
        self,
        lat: float,
        lng: float,
        radius_km: float = 10,
        min_complaints: int = 5,
        time_window_days: int = 30
    ) -> List[HotspotResult]:
        # TODO: Implement graph-based clustering
        raise NotImplementedError("KG teammate: Implement hotspot detection")
    
    async def get_department_performance(
        self,
        department_id: Optional[str] = None,
        time_window_days: int = 30
    ) -> List[Dict[str, Any]]:
        # TODO: Implement graph traversal for performance metrics
        raise NotImplementedError("KG teammate: Implement department analytics")
    
    async def get_related_complaints(
        self,
        complaint_id: str,
        max_results: int = 10
    ) -> List[Dict[str, Any]]:
        # TODO: Implement graph traversal for related entities
        raise NotImplementedError("KG teammate: Implement related complaints")
    
    async def update_complaint_status(
        self,
        complaint_id: str,
        new_status: str,
        resolution_data: Optional[Dict] = None
    ) -> bool:
        # TODO: Update node in graph
        raise NotImplementedError("KG teammate: Implement status update")
    
    async def link_complaints(
        self,
        complaint_id_1: str,
        complaint_id_2: str,
        relationship: str = "SIMILAR_TO",
        confidence: float = 1.0
    ) -> bool:
        # TODO: Create edge in graph
        raise NotImplementedError("KG teammate: Implement complaint linking")


# === Singleton accessor ===

_graphrag_instance: GraphRAGInterface = None


def get_graphrag() -> GraphRAGInterface:
    """
    Get GraphRAG instance.
    
    KG Teammate: When ready, change this to return MSGraphRAGClient.
    """
    global _graphrag_instance
    
    if _graphrag_instance is None:
        if settings.GRAPHRAG_ENDPOINT:
            # Use actual GraphRAG when configured
            _graphrag_instance = MSGraphRAGClient(
                endpoint=settings.GRAPHRAG_ENDPOINT,
                api_key=settings.GRAPHRAG_API_KEY
            )
        else:
            # Use stub for development
            _graphrag_instance = StubGraphRAG()
    
    return _graphrag_instance
