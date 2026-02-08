"""
Populate database with 200 complaints distributed evenly across departments.
Each department gets ~33 complaints, with 5-6 unsolved and rest resolved.
"""

import asyncio
import random
from datetime import datetime, timedelta, timezone
from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

MONGODB_URI = os.getenv("MONGODB_URI")

# Complaint templates with variety
COMPLAINT_TITLES = {
    "MCD": [
        "Garbage not collected for 3 days",
        "Overflowing dustbin on street",
        "Stray dogs menace in locality",
        "Dead animal on road",
        "Illegal dumping of construction waste",
        "Broken garbage bins",
        "Foul smell from garbage dump",
        "Street sweeping not done",
        "Waste segregation not followed",
        "Garbage collection vehicle not coming",
    ],
    "NDMC": [
        "Street light not working",
        "Pothole on main road",
        "Broken footpath",
        "Park maintenance required",
        "Water logging in area",
        "Tree branch fallen on road",
        "Illegal parking issue",
        "Public toilet not clean",
        "Broken park bench",
        "Damaged road divider",
    ],
    "PWD": [
        "Major pothole on highway",
        "Road resurfacing needed",
        "Bridge railing damaged",
        "Flyover maintenance required",
        "Road markings faded",
        "Traffic signal not working",
        "Speed breaker damaged",
        "Footpath encroachment",
        "Road accident spot needs signage",
        "Waterlogging during rain",
    ],
    "DDA": [
        "Illegal construction in park",
        "Unauthorized commercial activity",
        "Park encroachment issue",
        "DDA flat maintenance required",
        "Illegal tree cutting",
        "Parking lot not maintained",
        "Community center repair needed",
        "Green area being converted",
        "Unauthorized building extension",
        "Damaged boundary wall",
    ],
    "DMRC": [
        "Metro station escalator not working",
        "Ticket vending machine issue",
        "Station cleanliness problem",
        "AC not working in coach",
        "Metro delay issue",
        "Platform overcrowding",
        "Station toilet maintenance",
        "Missing signage at station",
        "Rude staff behavior",
        "Security concern at station",
    ],
    "DTC": [
        "Bus not following schedule",
        "Rude bus conductor",
        "Bus AC not working",
        "Overcrowded bus",
        "Bus stop shelter damaged",
        "Bus route information missing",
        "Dirty bus interior",
        "Bus driver rash driving",
        "Bus stop not maintained",
        "Long waiting time for bus",
    ],
}

LOCATIONS = [
    "Connaught Place", "Karol Bagh", "Dwarka Sector 10", "Rohini Sector 15",
    "Vasant Kunj", "Nehru Place", "Lajpat Nagar", "Saket", "Janakpuri",
    "Pitampura", "Mayur Vihar", "Preet Vihar", "Shahdara", "Model Town",
    "Rajouri Garden", "Punjabi Bagh", "Paschim Vihar", "Tilak Nagar",
    "Greater Kailash", "Defence Colony", "Hauz Khas", "Green Park",
    "Malviya Nagar", "R.K. Puram", "Vasant Vihar", "Chanakyapuri",
]


async def get_departments(db):
    """Fetch all departments from database."""
    departments = []
    async for dept in db.departments.find({}):
        departments.append(dept)
    return departments


async def get_categories_by_department(db, dept_id):
    """Get categories for a specific department."""
    categories = []
    async for cat in db.categories.find({"default_department_id": dept_id}):
        categories.append(cat)
    return categories


async def get_test_citizen(db):
    """Get or create test citizen."""
    citizen = await db.users.find_one({"phone": "9876543210"})
    if not citizen:
        print("Test citizen not found, creating one...")
        citizen_data = {
            "phone": "9876543210",
            "password_hash": "$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5LS2LG.KlHW3y",  # citizen123
            "role": "citizen",
            "name": "Test Citizen",
            "created_at": datetime.now(timezone.utc),
        }
        result = await db.users.insert_one(citizen_data)
        citizen = await db.users.find_one({"_id": result.inserted_id})
    return citizen


async def create_complaint(db, dept, category, citizen, title, location, is_resolved, days_ago):
    """Create a single complaint."""
    created_date = datetime.now(timezone.utc) - timedelta(days=days_ago)
    
    complaint_data = {
        "title": title,
        "description": f"Detailed complaint about: {title}. Location: {location}. Requires immediate attention from {dept['name']}.",
        "category": {
            "id": str(category["_id"]),
            "name": category["name"],
        },
        "department": {
            "id": str(dept["_id"]),
            "name": dept["name"],
        },
        "location": {
            "address": location,
            "landmark": f"Near {location}",
            "latitude": 28.6139 + random.uniform(-0.2, 0.2),
            "longitude": 77.2090 + random.uniform(-0.2, 0.2),
        },
        "citizen": {
            "id": str(citizen["_id"]),
            "name": citizen.get("name", "Anonymous"),
            "phone": citizen["phone"],
        },
        "status": "resolved" if is_resolved else "pending",
        "priority": random.choice(["low", "medium", "high"]),
        "media_urls": [],
        "created_at": created_date,
        "updated_at": created_date,
    }
    
    if is_resolved:
        resolved_date = created_date + timedelta(days=random.randint(1, 5))
        complaint_data["resolved_at"] = resolved_date
        complaint_data["updated_at"] = resolved_date
        complaint_data["resolution"] = f"Resolved: {title}. Action taken by {dept['name']}."
        # Add rating for resolved complaints
        complaint_data["rating"] = random.randint(3, 5)
    
    result = await db.complaints.insert_one(complaint_data)
    return result.inserted_id


async def populate_database():
    """Main function to populate database with 200 complaints."""
    print("Connecting to MongoDB...")
    client = AsyncIOMotorClient(
        MONGODB_URI,
        tlsAllowInvalidCertificates=True
    )
    db = client.nagrik
    
    try:
        # Get all departments
        print("Fetching departments...")
        departments = await get_departments(db)
        print(f"Found {len(departments)} departments")
        
        if len(departments) == 0:
            print("Error: No departments found in database!")
            return
        
        # Get test citizen
        citizen = await get_test_citizen(db)
        print(f"Using citizen: {citizen['name']} ({citizen['phone']})")
        
        # Calculate distribution
        total_complaints = 200
        complaints_per_dept = total_complaints // len(departments)
        extra_complaints = total_complaints % len(departments)
        
        print(f"\nGenerating {total_complaints} complaints...")
        print(f"Base complaints per department: {complaints_per_dept}")
        print(f"Extra complaints to distribute: {extra_complaints}\n")
        
        total_created = 0
        dept_stats = {}
        
        for idx, dept in enumerate(departments):
            dept_name = dept["name"]
            dept_id = dept["_id"]
            
            # Get categories for this department
            categories = await get_categories_by_department(db, dept_id)
            if not categories:
                print(f"Warning: No categories found for {dept_name}, skipping...")
                continue
            
            # Calculate complaints for this department
            num_complaints = complaints_per_dept
            if idx < extra_complaints:
                num_complaints += 1
            
            # Determine how many to leave unsolved (5-6 per department)
            num_unsolved = random.randint(5, 6)
            num_resolved = num_complaints - num_unsolved
            
            print(f"Department: {dept_name}")
            print(f"  Total: {num_complaints} complaints")
            print(f"  Resolved: {num_resolved}")
            print(f"  Unsolved: {num_unsolved}")
            
            # Get complaint titles for this department
            titles = COMPLAINT_TITLES.get(dept_name, [
                f"Issue {i+1} for {dept_name}" for i in range(10)
            ])
            
            created_count = 0
            
            # Create resolved complaints
            for i in range(num_resolved):
                title = random.choice(titles)
                location = random.choice(LOCATIONS)
                category = random.choice(categories)
                days_ago = random.randint(7, 60)  # Created 7-60 days ago
                
                await create_complaint(
                    db, dept, category, citizen, title, location,
                    is_resolved=True, days_ago=days_ago
                )
                created_count += 1
            
            # Create unsolved complaints
            for i in range(num_unsolved):
                title = random.choice(titles)
                location = random.choice(LOCATIONS)
                category = random.choice(categories)
                days_ago = random.randint(1, 14)  # Created 1-14 days ago
                
                await create_complaint(
                    db, dept, category, citizen, title, location,
                    is_resolved=False, days_ago=days_ago
                )
                created_count += 1
            
            dept_stats[dept_name] = {
                "total": num_complaints,
                "resolved": num_resolved,
                "unsolved": num_unsolved,
                "resolution_rate": (num_resolved / num_complaints * 100) if num_complaints > 0 else 0
            }
            
            total_created += created_count
            print(f"  Created: {created_count} complaints")
            print(f"  Resolution rate: {dept_stats[dept_name]['resolution_rate']:.1f}%\n")
        
        print("="*60)
        print(f"Database population complete!")
        print(f"Total complaints created: {total_created}")
        print("="*60)
        print("\nDepartment Summary:")
        for dept_name, stats in dept_stats.items():
            print(f"{dept_name:15} - Total: {stats['total']:3} | Resolved: {stats['resolved']:3} | "
                  f"Unsolved: {stats['unsolved']:2} | Rate: {stats['resolution_rate']:5.1f}%")
        
        # Verify database sync
        print("\nVerifying database sync...")
        total_in_db = await db.complaints.count_documents({})
        print(f"Total complaints in database: {total_in_db}")
        
        if total_in_db == total_created:
            print("✓ Database is properly synced!")
        else:
            print(f"⚠ Warning: Expected {total_created} but found {total_in_db} in database")
        
    finally:
        client.close()
        print("\nDatabase connection closed.")


if __name__ == "__main__":
    asyncio.run(populate_database())
