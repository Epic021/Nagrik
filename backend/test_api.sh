#!/bin/bash
# NAGRIK API Test Script
# Run this after starting the server: uvicorn app.main:app --reload --port 8000

BASE_URL="http://localhost:8000/api/v1"
TOKEN=""

echo "=== NAGRIK API Test Suite ==="
echo ""

# 1. Health Check
echo "1. Health Check"
curl -s "$BASE_URL/health" | jq
echo ""

# 2. Get Categories
echo "2. Get Categories"
curl -s "$BASE_URL/categories" | jq '.[0:3]'
echo ""

# 3. Get Departments
echo "3. Get Departments"
curl -s "$BASE_URL/departments" | jq '.[0:3]'
echo ""

# 4. Register User
echo "4. Register User"
REGISTER_RESPONSE=$(curl -s -X POST "$BASE_URL/auth/register" \
  -H "Content-Type: application/json" \
  -d '{"name":"Test User","phone":"9876543210","password":"test123"}')
echo $REGISTER_RESPONSE | jq
echo ""

# 5. Login
echo "5. Login"
LOGIN_RESPONSE=$(curl -s -X POST "$BASE_URL/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"phone":"9876543210","password":"test123"}')
TOKEN=$(echo $LOGIN_RESPONSE | jq -r '.access_token')
echo "Token: ${TOKEN:0:50}..."
echo ""

# 6. Get Profile
echo "6. Get Profile"
curl -s "$BASE_URL/auth/me" -H "Authorization: Bearer $TOKEN" | jq
echo ""

# 7. Create Complaint
echo "7. Create Complaint"
COMPLAINT_RESPONSE=$(curl -s -X POST "$BASE_URL/complaints" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "title": "Pothole on MG Road",
    "description": "Large pothole causing accidents near metro station",
    "category_id": "potholes",
    "location": {"lat": 28.6139, "lng": 77.2090, "address": "MG Road, Delhi"},
    "urgency": "high"
  }')
COMPLAINT_ID=$(echo $COMPLAINT_RESPONSE | jq -r '.id')
echo $COMPLAINT_RESPONSE | jq
echo "Complaint ID: $COMPLAINT_ID"
echo ""

# 8. List Complaints
echo "8. List Complaints"
curl -s "$BASE_URL/complaints" -H "Authorization: Bearer $TOKEN" | jq '.complaints[0]'
echo ""

# 9. Upvote Complaint
echo "9. Upvote Complaint"
curl -s -X POST "$BASE_URL/complaints/$COMPLAINT_ID/upvote" \
  -H "Authorization: Bearer $TOKEN" | jq
echo ""

# 10. Test Duplicate Detection (submit similar complaint)
echo "10. Test Duplicate Detection (similar complaint)"
curl -s -X POST "$BASE_URL/complaints" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "title": "Road damage near MG Road metro",
    "description": "Big hole in the road",
    "category_id": "potholes",
    "location": {"lat": 28.6140, "lng": 77.2091, "address": "MG Road, Delhi"},
    "urgency": "medium"
  }' | jq
echo ""

# 11. Get Leaderboards
echo "11. Department Leaderboards"
curl -s "$BASE_URL/leaderboards/departments" | jq '.[0:2]'
echo ""

# 12. Get Hotspots
echo "12. Hotspots"
curl -s "$BASE_URL/leaderboards/hotspots?lat=28.6139&lng=77.2090" | jq
echo ""

# 13. Validate Location
echo "13. Validate Delhi Location"
curl -s "$BASE_URL/geo/validate?lat=28.6139&lng=77.2090" | jq
echo ""

# 14. AI Classification (requires GEMINI_API_KEY)
echo "14. AI Text Classification"
curl -s -X POST "$BASE_URL/classify/from-text" \
  -H "Content-Type: application/json" \
  -d '{"title": "Garbage piling up", "description": "Waste not collected for 3 days"}' | jq
echo ""

echo "=== Tests Complete ==="
echo ""
echo "Complaint ID for manual testing: $COMPLAINT_ID"
echo "Token for manual testing: $TOKEN"
