# Knowledge Graph (MS GraphRAG) Integration Guide

## Overview

The NAGRIK backend uses MS GraphRAG for:
- **Semantic duplicate detection** (smarter than text similarity)
- **Hotspot detection** (geographic clustering of complaints)
- **Department performance analysis** (graph-based metrics)
- **Related complaint discovery** (graph traversal)

Your implementation goes in: `app/api/services/graphrag.py`

---

## Setup

### 1. Install Dependencies
```bash
pip install graphrag
# Or add to requirements.txt
```

### 2. Configure Environment
Add to `.env`:
```
GRAPHRAG_ENDPOINT=http://localhost:8080
GRAPHRAG_API_KEY=your-api-key
```

### 3. Initialize GraphRAG Index

Create index with these entities:

| Entity | Properties |
|--------|------------|
| **Complaint** | id, title, description, category_id, department_id, urgency, status, created_at |
| **Location** | lat, lng, address, locality, ward |
| **Department** | id, name, short_name, contact_phone |
| **Category** | id, name, icon |

Relationships:
```
Complaint -[LOCATED_AT]-> Location
Complaint -[ASSIGNED_TO]-> Department
Complaint -[HAS_CATEGORY]-> Category
Complaint -[SIMILAR_TO {confidence: float}]-> Complaint
Complaint -[RESOLVED_BY]-> Resolution
Location -[NEARBY {distance_m: int}]-> Location
```

---

## What to Implement

Replace the `MSGraphRAGClient` methods in `graphrag.py`:

### 1. `add_complaint(complaint_data)` 
Called when a new complaint is created.

**Input:**
```python
{
    "id": "65abc123...",
    "title": "Pothole on MG Road",
    "description": "Large pothole causing accidents",
    "category_id": "potholes",
    "department_id": "mcd",
    "location": {"lat": 28.6139, "lng": 77.2090, "address": "..."},
    "urgency": "high",
    "created_at": datetime
}
```

**Your job:** Index this in GraphRAG, create entity nodes and relationships.

---

### 2. `find_duplicates(title, description, category_id, lat, lng, radius_meters)`
Called before creating a complaint to check for semantic duplicates.

**Expected behavior:**
- Use GraphRAG semantic search on title+description
- Filter by location (within radius_meters)
- Filter by category
- Return top matches with confidence scores

**Return:**
```python
[
    DuplicateResult(
        is_duplicate=True,
        confidence=0.85,
        original_complaint_id="65xyz...",
        similarity_score=0.9,
        merge_recommended=True
    )
]
```

**Why this matters:** Current system uses simple text similarity. GraphRAG can find:
- "Road has big hole" as duplicate of "Pothole on street"
- "Electricity went" as duplicate of "Power outage"

---

### 3. `get_hotspots(lat, lng, radius_km, min_complaints, time_window_days)`
Called by leaderboards to find problem areas.

**Expected behavior:**
- Use graph clustering to find dense complaint areas
- Filter by time window
- Calculate dominant category per cluster

**Return:**
```python
[
    HotspotResult(
        center_lat=28.62,
        center_lng=77.21,
        radius_meters=150,
        complaint_count=25,
        dominant_category="garbage",
        severity_score=0.8,
        trend="increasing"
    )
]
```

---

### 4. `get_department_performance(department_id, time_window_days)`
Called by leaderboards for department rankings.

**Expected behavior:**
- Traverse graph: Department <- RESOLVED_BY <- Complaint
- Calculate: resolution_rate, avg_time, citizen_satisfaction

**Return:**
```python
[
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
```

---

### 5. `get_related_complaints(complaint_id, max_results)`
Called to show related issues on complaint detail page.

**Expected behavior:**
- Find SIMILAR_TO relationships
- Find NEARBY complaints
- Find same DEPARTMENT complaints

---

## Where Your Code Gets Called

| Backend File | When | GraphRAG Method |
|--------------|------|-----------------|
| `complaints.py` | New complaint created | `add_complaint()`, `find_duplicates()` |
| `leaderboards.py` | `/leaderboards/hotspots` | `get_hotspots()` |
| `leaderboards.py` | `/leaderboards/departments` | `get_department_performance()` |
| `ai.py` | `/ai/similar/{id}` | `get_related_complaints()` |
| `complaints.py` | Status changed | `update_complaint_status()` |

---

## Testing

1. Start GraphRAG server
2. Set `GRAPHRAG_ENDPOINT` in `.env`
3. Restart backend: `uvicorn app.main:app --reload`
4. Create complaints via API
5. Check GraphRAG logs for indexed data
6. Query `/api/v1/leaderboards/hotspots` to test

---

## Current Stub Behavior

The `StubGraphRAG` class returns mock data. When you implement `MSGraphRAGClient`, it will automatically be used when `GRAPHRAG_ENDPOINT` is set.

The switch happens in `get_graphrag()`:
```python
if settings.GRAPHRAG_ENDPOINT:
    return MSGraphRAGClient(...)  # Your implementation
else:
    return StubGraphRAG()  # Mock data
```
