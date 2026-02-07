# Admin Dashboard Integration Guide

## Overview

The admin dashboard provides department-specific management of civic complaints. Each department admin sees only their department's complaints, while super admins see everything.

---

## Authentication

### Super Admin (Pre-seeded)
```
Phone: 9999999999
Password: admin123
```

### Login as Admin
```javascript
POST /api/v1/auth/login
{
  "phone": "9999999999",
  "password": "admin123"
}
// Response: { "access_token": "...", "user": { "role": "super_admin" } }
```

### Create Department Admin (Super Admin Only)
```javascript
POST /api/v1/admin/register
Headers: Authorization: Bearer <super_admin_token>
{
  "name": "MCD Admin",
  "phone": "9876543211",
  "password": "mcd123",
  "department_id": "mcd"
}
```

---

## Admin API Endpoints

### Dashboard Stats
```javascript
GET /api/v1/admin/dashboard
Headers: Authorization: Bearer <admin_token>

// Response:
{
  "department_id": "mcd",
  "summary": {
    "total_complaints": 150,
    "today_new": 12,
    "week_new": 45,
    "week_resolved": 38,
    "high_urgency_pending": 5
  },
  "by_status": {
    "pending": 25,
    "assigned": 15,
    "in_progress": 20,
    "resolved": 85,
    "rejected": 3,
    "citizen_rejected": 2
  },
  "performance": {
    "resolution_rate": 56.7,
    "satisfaction_rate": 92.5,
    "avg_resolution_hours": 48.5
  },
  "top_categories": [
    { "category": "Potholes", "count": 45 },
    { "category": "Garbage", "count": 32 }
  ]
}
```

### Dashboard Trends (For Charts)
```javascript
GET /api/v1/admin/dashboard/trends?days=30

// Response:
{
  "period_days": 30,
  "new_complaints": [
    { "date": "2024-01-01", "count": 5 },
    { "date": "2024-01-02", "count": 8 }
  ],
  "resolutions": [
    { "date": "2024-01-01", "count": 3 },
    { "date": "2024-01-02", "count": 6 }
  ]
}
```

### List Department Complaints
```javascript
GET /api/v1/admin/complaints?status=pending&urgency=high&page=1&limit=20&sort_by=urgency

// Response:
{
  "complaints": [...],
  "total": 45,
  "page": 1,
  "pages": 3
}
```

### Get Complaint Detail
```javascript
GET /api/v1/admin/complaints/{complaint_id}

// Response includes full details + history
{
  "id": "...",
  "title": "...",
  "history": [
    { "action": "status_changed", "by": {...}, "notes": "...", "created_at": "..." }
  ]
}
```

---

## Complaint Actions

### Update Status
```javascript
PUT /api/v1/admin/complaints/{id}/status
{
  "status": "in_progress",  // pending, assigned, in_progress, resolved, rejected
  "notes": "Team dispatched"
}
```

### Assign to Staff
```javascript
PUT /api/v1/admin/complaints/{id}/assign
{
  "assigned_to_name": "Ramesh Kumar",
  "assigned_to_phone": "9876543212",
  "priority": "high"  // low, normal, high, urgent
}
```

### Mark as Resolved
```javascript
PUT /api/v1/admin/complaints/{id}/resolve
{
  "resolution_notes": "Pothole filled and road repaired. Inspected on site.",
  "resolved_by_name": "Field Team A"
}
```

### Escalate
```javascript
PUT /api/v1/admin/complaints/{id}/escalate
{
  "reason": "Requires heavy machinery, beyond local team capacity"
}
```

### Reject Complaint
```javascript
PUT /api/v1/admin/complaints/{id}/reject?reason=Location%20outside%20jurisdiction
```

---

## Bulk Operations

### Bulk Assign
```javascript
POST /api/v1/admin/complaints/bulk-assign
{
  "complaint_ids": ["id1", "id2", "id3"],
  "assigned_to_name": "Field Team B",
  "priority": "high"
}
```

### Bulk Status Update
```javascript
POST /api/v1/admin/complaints/bulk-status
{
  "complaint_ids": ["id1", "id2"],
  "new_status": "in_progress"
}
```

---

## Roles & Permissions

| Action | Citizen | Dept Admin | Super Admin |
|--------|---------|------------|-------------|
| Submit complaint | ✅ | ✅ | ✅ |
| View all complaints | ✅ | ❌ (own dept only) | ✅ |
| Update status | ❌ | ✅ (own dept) | ✅ |
| Resolve complaint | ❌ | ✅ (own dept) | ✅ |
| Assign staff | ❌ | ✅ (own dept) | ✅ |
| Create dept admin | ❌ | ❌ | ✅ |
| View dashboard | ❌ | ✅ (own dept) | ✅ |

---

## Admin UI Components Needed

1. **Login Page** - Separate admin login
2. **Dashboard Home**
   - Summary cards (new today, pending, high urgency)
   - Status breakdown chart
   - Resolution rate gauge
   - Top categories chart
   - Trends line chart (new vs resolved)
3. **Complaints List**
   - Filterable table (status, urgency, date)
   - Bulk selection for bulk actions
   - Quick status update dropdown
4. **Complaint Detail**
   - Full complaint info
   - Media gallery
   - Location map
   - Action buttons (assign, resolve, escalate, reject)
   - History timeline
5. **Staff/Assignment Panel**
   - Assign to field worker
   - Set priority
6. **Settings** (Super Admin)
   - Create department admins
   - Manage departments

---

## Department IDs for Reference

| ID | Department |
|----|------------|
| mcd | Municipal Corporation of Delhi |
| pwd | Public Works Department |
| djb | Delhi Jal Board |
| bses | BSES Electricity |
| ndmc | New Delhi Municipal Council |
| dda | Delhi Development Authority |
| dpcc | Delhi Pollution Control |
| dttdc | Delhi Traffic Police |
| dmrc | Delhi Metro Rail Corporation |
| forest | Delhi Forest Department |
| health | Health Department |
| education | Education Department |
