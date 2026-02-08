"""
Generate sample complaints for each department
"""
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import os
from datetime import datetime, timezone, timedelta
import random
from dotenv import load_dotenv

load_dotenv()

async def generate_complaints():
    mongodb_uri = os.getenv("MONGODB_URI")
    client = AsyncIOMotorClient(mongodb_uri, tlsAllowInvalidCertificates=True)
    db = client.nagrik
    
    # Department-specific complaint templates
    dept_complaints = {
        "mcd": [
            {"title": "Overflowing garbage bin at Connaught Place", "category": "Waste Management", "description": "Garbage bin overflowing for 3 days"},
            {"title": "Street dog menace in Karol Bagh", "category": "Animal Control", "description": "Stray dogs attacking pedestrians"},
            {"title": "Illegal construction on MG Road", "category": "Building Violations", "description": "Unauthorized construction without permits"},
            {"title": "Broken footpath near India Gate", "category": "Infrastructure", "description": "Footpath damaged and dangerous"},
            {"title": "Water logging in Dwarka Sector 10", "category": "Drainage", "description": "Severe waterlogging after rain"},
            {"title": "Unclean public toilet at Central Park", "category": "Sanitation", "description": "Public toilet in unhygienic condition"},
            {"title": "Illegal parking blocking road", "category": "Traffic", "description": "Cars parked on main road causing congestion"},
            {"title": "Dead tree about to fall in Rohini", "category": "Public Safety", "description": "Large dead tree posing danger"},
            {"title": "Mosquito breeding in park", "category": "Health", "description": "Stagnant water causing mosquito problem"},
            {"title": "Missing manhole cover in Pitampura", "category": "Public Safety", "description": "Open manhole without cover - dangerous"},
            {"title": "Garbage not collected for a week", "category": "Waste Management", "description": "Regular garbage collection stopped"},
            {"title": "Encroachment on public land", "category": "Land Management", "description": "Illegal shops on footpath"},
            {"title": "Broken playground equipment", "category": "Parks", "description": "Children's park equipment damaged"},
            {"title": "Polluted pond in neighborhood", "category": "Environment", "description": "Local pond filled with sewage"},
            {"title": "Unauthorized hoardings on road", "category": "Advertising", "description": "Illegal billboards blocking view"}
        ],
        "ndmc": [
            {"title": "Potholes on Rajpath", "category": "Roads", "description": "Multiple potholes near India Gate area"},
            {"title": "Street light not working on Barakhamba Road", "category": "Street Lights", "description": "Dark area at night - safety concern"},
            {"title": "Water supply issue in Khan Market", "category": "Water Supply", "description": "No water for 2 days"},
            {"title": "Damaged park bench in Lodhi Garden", "category": "Parks", "description": "Broken benches need replacement"},
            {"title": "Malfunctioning traffic signal", "category": "Traffic", "description": "Signal stuck on red at CP crossing"},
            {"title": "Blocked drain on Janpath", "category": "Drainage", "description": "Water overflow during rain"},
            {"title": "Fallen tree branch on road", "category": "Public Safety", "description": "Tree debris blocking traffic"},
            {"title": "Damaged road sign at roundabout", "category": "Signage", "description": "Important road sign broken"},
            {"title": "Unauthorized vendors near metro", "category": "Encroachment", "description": "Blocking pedestrian pathway"},
            {"title": "Public fountain not working", "category": "Infrastructure", "description": "Monument fountain needs repair"},
            {"title": "Unclean bus stop area", "category": "Sanitation", "description": "Litter and garbage accumulation"},
            {"title": "Broken pavement tiles", "category": "Infrastructure", "description": "Pedestrian area unsafe"},
            {"title": "Stray cattle on main road", "category": "Animal Control", "description": "Traffic disruption by cattle"},
            {"title": "Poor drainage in parking lot", "category": "Drainage", "description": "Water accumulation problem"},
            {"title": "Damaged boundary wall", "category": "Infrastructure", "description": "Public property wall broken"}
        ],
        "pwd": [
            {"title": "Major pothole on NH-48", "category": "Roads", "description": "Deep pothole causing accidents"},
            {"title": "Bridge repair needed urgently", "category": "Bridges", "description": "Cracks visible on flyover"},
            {"title": "Damaged divider on Ring Road", "category": "Roads", "description": "Road divider broken at multiple points"},
            {"title": "Street light pole fallen", "category": "Street Lights", "description": "Electric pole lying on road"},
            {"title": "Road flooding in underpass", "category": "Drainage", "description": "Underpass completely waterlogged"},
            {"title": "Missing road signs on highway", "category": "Signage", "description": "Direction boards removed"},
            {"title": "Broken speed breaker", "category": "Roads", "description": "Speed bump damaged - hazardous"},
            {"title": "Illegal speed breaker installed", "category": "Roads", "description": "Unauthorized bump causing accidents"},
            {"title": "Road cave-in near mall", "category": "Public Safety", "description": "Road surface collapsing"},
            {"title": "Overflowing sewer on main road", "category": "Sanitation", "description": "Sewage water on street"},
            {"title": "Damaged footover bridge", "category": "Bridges", "description": "Pedestrian bridge needs repair"},
            {"title": "Fallen trees blocking highway", "category": "Public Safety", "description": "Storm damage - road blocked"},
            {"title": "Poor road markings", "category": "Roads", "description": "Lane markings completely faded"},
            {"title": "Bus shelter damaged", "category": "Infrastructure", "description": "Public transport shelter broken"},
            {"title": "Accident-prone curve needs safety", "category": "Public Safety", "description": "Dangerous turn needs barriers"}
        ],
        "dda": [
            {"title": "Illegal construction in DDA park", "category": "Land Management", "description": "Unauthorized structure in park"},
            {"title": "Encroachment on DDA land", "category": "Land Management", "description": "Private parties occupying public land"},
            {"title": "Park maintenance required", "category": "Parks", "description": "Overgrown vegetation and broken equipment"},
            {"title": "Playground equipment broken", "category": "Parks", "description": "Children's play area unsafe"},
            {"title": "DDA flat water leakage", "category": "Housing", "description": "Seepage from upper floor"},
            {"title": "Common area not maintained", "category": "Housing", "description": "Society common spaces dirty"},
            {"title": "Street vendor encroachment", "category": "Encroachment", "description": "Vendors blocking DDA pathways"},
            {"title": "Park lighting not working", "category": "Infrastructure", "description": "Dark park - safety issue"},
            {"title": "Damaged community center", "category": "Infrastructure", "description": "Public facility needs repair"},
            {"title": "Illegal parking in DDA area", "category": "Traffic", "description": "Blocking emergency access"},
            {"title": "Unauthorized tree cutting", "category": "Environment", "description": "Trees being cut without permission"},
            {"title": "Broken boundary wall of park", "category": "Infrastructure", "description": "Security concern for park"},
            {"title": "Polluted lake in DDA colony", "category": "Environment", "description": "Water body contaminated"},
            {"title": "Missing park gate", "category": "Infrastructure", "description": "Park entrance without gate"},
            {"title": "Damaged sports facility", "category": "Sports", "description": "Tennis court needs resurfacing"}
        ],
        "dmrc": [
            {"title": "Metro escalator not working", "category": "Infrastructure", "description": "Escalator at CP metro station broken"},
            {"title": "Broken ticket vending machine", "category": "Infrastructure", "description": "Cannot buy tokens"},
            {"title": "Metro station toilet unclean", "category": "Sanitation", "description": "Washroom in poor condition"},
            {"title": "Air conditioning not working", "category": "Comfort", "description": "Train AC malfunctioning"},
            {"title": "Platform announcement system faulty", "category": "Infrastructure", "description": "Cannot hear announcements"},
            {"title": "Elevator not functioning", "category": "Accessibility", "description": "Disabled access not available"},
            {"title": "Metro coach door malfunction", "category": "Safety", "description": "Door not closing properly"},
            {"title": "Station signage missing", "category": "Signage", "description": "Direction boards removed"},
            {"title": "Leaking ceiling at station", "category": "Infrastructure", "description": "Water dripping on platform"},
            {"title": "Broken seats in metro coach", "category": "Comfort", "description": "Damaged seating"},
            {"title": "Poor lighting at station", "category": "Infrastructure", "description": "Dark areas - safety concern"},
            {"title": "Crowded platform - safety risk", "category": "Safety", "description": "Overcrowding during peak hours"},
            {"title": "Metro card recharge issue", "category": "Infrastructure", "description": "Top-up machines not working"},
            {"title": "Damaged platform tiles", "category": "Infrastructure", "description": "Broken floor tiles - trip hazard"},
            {"title": "Emergency exit blocked", "category": "Safety", "description": "Fire exit obstructed"}
        ],
        "dtc": [
            {"title": "Bus not arriving on time", "category": "Service", "description": "Route 534 irregular schedule"},
            {"title": "Broken bus shelter", "category": "Infrastructure", "description": "No protection from weather"},
            {"title": "Bus AC not working", "category": "Comfort", "description": "Hot and uncomfortable journey"},
            {"title": "Rash driving by bus driver", "category": "Safety", "description": "Dangerous driving behavior"},
            {"title": "Bus stop sign missing", "category": "Signage", "description": "Cannot identify bus stop"},
            {"title": "Dirty bus interior", "category": "Sanitation", "description": "Bus not cleaned regularly"},
            {"title": "Bus seat broken", "category": "Infrastructure", "description": "Damaged seating"},
            {"title": "No buses on route for hours", "category": "Service", "description": "Route 987 service stopped"},
            {"title": "Bus door not closing", "category": "Safety", "description": "Safety hazard while moving"},
            {"title": "Overcharging by conductor", "category": "Service", "description": "Asked for extra fare"},
            {"title": "Bus shelter bench broken", "category": "Infrastructure", "description": "No seating at stop"},
            {"title": "Irregular frequency on route", "category": "Service", "description": "Long waiting times"},
            {"title": "Broken display board", "category": "Infrastructure", "description": "Route information not visible"},
            {"title": "Unsafe bus condition", "category": "Safety", "description": "Old bus in poor state"},
            {"title": "No bus info at new stop", "category": "Signage", "description": "Newly created stop lacks signage"}
        ]
    }
    
    locations = [
        "Connaught Place", "India Gate", "Karol Bagh", "Dwarka Sector 10", "Rohini",
        "Pitampura", "Khan Market", "Lodhi Garden", "Janpath", "MG Road",
        "Central Park", "Rajpath", "Barakhamba Road", "Ring Road", "NH-48",
        "Nehru Place", "Saket", "Vasant Kunj", "Green Park", "Hauz Khas"
    ]
    
    urgency_levels = ["low", "medium", "high", "urgent"]
    statuses = ["pending", "in_progress", "resolved"]
    
    # Get a test citizen for creating complaints
    citizen = await db.users.find_one({"role": "citizen"})
    if not citizen:
        # Create a test citizen if not exists
        citizen_data = {
            "phone": "9999999999",
            "password_hash": "$2b$12$dummy_hash",
            "name": "Test Citizen",
            "email": "citizen@test.com",
            "role": "citizen",
            "is_active": True,
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc)
        }
        result = await db.users.insert_one(citizen_data)
        citizen = await db.users.find_one({"_id": result.inserted_id})
    
    total_created = 0
    
    for dept_id, complaints in dept_complaints.items():
        print(f"\nCreating complaints for {dept_id.upper()}...")
        
        for i, complaint_template in enumerate(complaints):
            now = datetime.now(timezone.utc)
            # Vary creation time over the last 7 days
            created_at = now - timedelta(days=random.randint(0, 7), hours=random.randint(0, 23))
            
            # Assign random status with bias towards pending
            status_weights = [0.4, 0.3, 0.3]  # 40% pending, 30% in_progress, 30% resolved
            status = random.choices(statuses, weights=status_weights)[0]
            
            complaint_data = {
                "title": complaint_template["title"],
                "description": complaint_template["description"],
                "category": {
                    "id": complaint_template["category"].lower().replace(" ", "_"),
                    "name": complaint_template["category"],
                    "icon": "🔧"
                },
                "department": {
                    "id": dept_id,
                    "name": get_dept_name(dept_id),
                    "short_name": dept_id.upper()
                },
                "location": {
                    "address": random.choice(locations),
                    "coordinates": {
                        "latitude": 28.6139 + random.uniform(-0.1, 0.1),
                        "longitude": 77.2090 + random.uniform(-0.1, 0.1)
                    }
                },
                "citizen": {
                    "id": str(citizen["_id"]),
                    "name": citizen["name"],
                    "phone": citizen["phone"]
                },
                "status": status,
                "urgency": random.choice(urgency_levels),
                "upvote_count": random.randint(0, 50),
                "media": [],
                "created_at": created_at,
                "updated_at": created_at,
                "resolved_at": created_at + timedelta(hours=random.randint(2, 48)) if status == "resolved" else None,
                "resolution_details": f"Issue resolved successfully" if status == "resolved" else None
            }
            
            await db.complaints.insert_one(complaint_data)
            total_created += 1
            print(f"  ✓ Created: {complaint_template['title'][:50]}... ({status})")
    
    print(f"\n{'='*60}")
    print(f"Total complaints created: {total_created}")
    print(f"{'='*60}")
    
    client.close()

def get_dept_name(dept_id):
    names = {
        "mcd": "Municipal Corporation of Delhi",
        "ndmc": "New Delhi Municipal Council",
        "pwd": "Public Works Department",
        "dda": "Delhi Development Authority",
        "dmrc": "Delhi Metro Rail Corporation",
        "dtc": "Delhi Transport Corporation"
    }
    return names.get(dept_id, dept_id.upper())

if __name__ == "__main__":
    asyncio.run(generate_complaints())
