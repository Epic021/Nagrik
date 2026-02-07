# NAGRIK Frontend Integration Guide (Complete)

## API Base URL
```
Development: http://localhost:8000/api/v1
Production: https://your-domain.com/api/v1
```

Swagger Docs: http://localhost:8000/docs

---

# PART 1: CITIZEN APP

## Authentication

### Register
```javascript
POST /auth/register
{ "name": "Rahul", "phone": "9876543210", "password": "secure123" }
→ { "id": "...", "name": "...", "role": "citizen" }
```

### Login
```javascript
POST /auth/login
{ "phone": "9876543210", "password": "secure123" }
→ { "access_token": "eyJ...", "user": {...} }
```

### Get Profile
```javascript
GET /auth/me
Headers: Authorization: Bearer <token>
```

---

## Complaint Submission Flow

### Step 1: Upload Image
```javascript
POST /files/upload (multipart/form-data)
→ { "url": "https://storage.googleapis.com/..." }
```

### Step 2: AI Classification
```javascript
// From image:
POST /classify/from-image
{ "image_url": "...", "description": "optional" }

// From text:
POST /classify/from-text
{ "title": "...", "description": "..." }

→ { "category_id": "potholes", "confidence": 0.92, "suggested_urgency": "high" }
```

### Step 3: Get Location
```javascript
// Validate coordinates:
GET /geo/validate?lat=28.6139&lng=77.2090

// Get address from coords:
GET /geo/reverse?lat=28.6139&lng=77.2090

// Get coords from address:
GET /geo/geocode?address=MG%20Road%20Delhi
```

### Step 4: Submit Complaint
```javascript
POST /complaints
{
  "title": "Pothole on MG Road",
  "description": "Large pothole near metro",
  "category_id": "potholes",
  "location": { "lat": 28.6139, "lng": 77.2090, "address": "..." },
  "media_urls": ["..."],
  "urgency": "high"
}
→ { "id": "...", "department": {...}, "status": "pending" }
```

---

## Feed & Discovery

### List Complaints (Public Feed)
```javascript
GET /complaints?lat=28.6&lng=77.2&radius=10&sort=upvotes&page=1&limit=20
GET /complaints?category_id=potholes&status=pending
```

### My Complaints
```javascript
GET /complaints/my
```

### Complaint Detail
```javascript
GET /complaints/{id}
```

---

## User Actions

### Upvote
```javascript
POST /complaints/{id}/upvote    // Add
DELETE /complaints/{id}/upvote  // Remove
```

### Verify Resolution (Creator Only)
```javascript
POST /complaints/{id}/verify
{ "accepted": true, "feedback": "Fixed properly" }
```

---

## Reference Data

### Categories
```javascript
GET /categories
→ [{ "id": "potholes", "name": "Potholes", "icon": "🕳️" }, ...]
```

### Departments
```javascript
GET /departments
→ [{ "id": "mcd", "name": "MCD", "short_name": "MCD" }, ...]
```

---

## Leaderboards

```javascript
GET /leaderboards/departments  // Department rankings
GET /leaderboards/issues?lat=28.6&lng=77.2  // Top issues nearby
GET /leaderboards/hotspots?lat=28.6&lng=77.2  // Problem areas
```

---

# PART 2: ADMIN DASHBOARD

## Admin Authentication

### Super Admin (Default)
```
Phone: 9999999999
Password: admin123
```

### Login (Same Endpoint)
```javascript
POST /auth/login
{ "phone": "9999999999", "password": "admin123" }
→ { "access_token": "...", "user": { "role": "super_admin" } }
```

Check `user.role` to determine UI:
- `citizen` → Citizen app
- `department_admin` → Dept dashboard
- `super_admin` → Full admin

---

## Admin Dashboard APIs

### Dashboard Stats
```javascript
GET /admin/dashboard
→ {
  "summary": { "total_complaints": 150, "today_new": 12, "high_urgency_pending": 5 },
  "by_status": { "pending": 25, "resolved": 85, ... },
  "performance": { "resolution_rate": 56.7, "satisfaction_rate": 92.5 },
  "top_categories": [{ "category": "Potholes", "count": 45 }]
}
```

### Trends (For Charts)
```javascript
GET /admin/dashboard/trends?days=30
→ { "new_complaints": [...], "resolutions": [...] }
```

### Department Complaints
```javascript
GET /admin/complaints?status=pending&urgency=high&page=1
```

### Complaint Detail (With History)
```javascript
GET /admin/complaints/{id}
→ { ... "history": [{ "action": "assigned", "by": {...}, "created_at": "..." }] }
```

---

## Admin Actions

### Update Status
```javascript
PUT /admin/complaints/{id}/status
{ "status": "in_progress", "notes": "Team dispatched" }
```

### Assign Staff
```javascript
PUT /admin/complaints/{id}/assign
{ "assigned_to_name": "Ramesh", "priority": "high" }
```

### Resolve
```javascript
PUT /admin/complaints/{id}/resolve
{ "resolution_notes": "Pothole repaired", "resolved_by_name": "Team A" }
```

### Escalate
```javascript
PUT /admin/complaints/{id}/escalate
{ "reason": "Needs heavy machinery" }
```

### Reject
```javascript
PUT /admin/complaints/{id}/reject?reason=Outside%20jurisdiction
```

---

## Bulk Operations

```javascript
POST /admin/complaints/bulk-assign
{ "complaint_ids": ["id1", "id2"], "assigned_to_name": "Team B" }

POST /admin/complaints/bulk-status
{ "complaint_ids": ["id1", "id2"], "new_status": "in_progress" }
```

---

## Create Department Admin (Super Admin Only)

```javascript
POST /admin/register
{ "name": "MCD Admin", "phone": "9876543211", "password": "mcd123", "department_id": "mcd" }
```

---

# PART 3: UI SCREENS NEEDED

## Citizen App
| Screen | Key Features |
|--------|--------------|
| Login/Register | Phone + password auth |
| Home Feed | Map view + list, filter by category/status |
| Complaint Detail | Status, upvotes, location, media |
| Submit Flow | Image → AI classify → Location → Confirm |
| My Complaints | User's submissions + status |
| Leaderboards | Department rankings, top issues |
| Profile | User info, logout |

## Admin Dashboard
| Screen | Key Features |
|--------|--------------|
| Dashboard Home | Stats cards, charts, trends |
| Complaints List | Filterable table with bulk actions |
| Complaint Detail | Full info + actions + history timeline |
| Staff Assignment | Assign workers, set priority |
| Admin Management | Create dept admins (super only) |

---

# PART 4: STATUS REFERENCE

| Status | Meaning | Color |
|--------|---------|-------|
| pending | New, awaiting action | 🟡 Yellow |
| assigned | Sent to field worker | 🔵 Blue |
| in_progress | Work started | 🟠 Orange |
| resolved | Dept marked done | 🟢 Green |
| citizen_rejected | Citizen rejected fix | 🔴 Red |
| rejected | Dept rejected complaint | ⚫ Gray |

---

# PART 5: ERROR HANDLING

```javascript
// All errors return:
{ "detail": "Error message" }

// Status codes:
400 - Bad request (validation failed)
401 - Not authenticated
403 - Forbidden (wrong role)
404 - Not found
500 - Server error
```

---

# PART 6: TIPS

1. **Store token** in localStorage/SecureStore
2. **Check role** on login to route to correct UI
3. **Show AI confidence** when suggesting category
4. **Highlight merged complaints** ("Added to existing issue")
5. **Color-code status** badges
6. **Show upvote count** prominently
7. **Use map** for location selection + hotspots
8. **Optimistic updates** for upvotes
