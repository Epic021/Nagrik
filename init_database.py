"""
Initialize database with departments and categories.
"""
import asyncio
import os
from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId
from dotenv import load_dotenv

load_dotenv()

MONGODB_URI = os.getenv("MONGODB_URI")

# Department data
DEPARTMENTS = [
    {
        "name": "MCD",
        "full_name": "Municipal Corporation of Delhi",
        "description": "Handles garbage collection, sanitation, and waste management",
        "contact": {
            "email": "mcd@delhi.gov.in",
            "phone": "1800-11-6688"
        }
    },
    {
        "name": "NDMC",
        "full_name": "New Delhi Municipal Council",
        "description": "Manages civic services in New Delhi area",
        "contact": {
            "email": "ndmc@delhi.gov.in",
            "phone": "1800-11-3344"
        }
    },
    {
        "name": "PWD",
        "full_name": "Public Works Department",
        "description": "Maintains roads, bridges, and public infrastructure",
        "contact": {
            "email": "pwd@delhi.gov.in",
            "phone": "1800-11-5577"
        }
    },
    {
        "name": "DDA",
        "full_name": "Delhi Development Authority",
        "description": "Urban planning and development",
        "contact": {
            "email": "dda@delhi.gov.in",
            "phone": "1800-11-2233"
        }
    },
    {
        "name": "DMRC",
        "full_name": "Delhi Metro Rail Corporation",
        "description": "Metro rail services and infrastructure",
        "contact": {
            "email": "dmrc@delhi.gov.in",
            "phone": "155370"
        }
    },
    {
        "name": "DTC",
        "full_name": "Delhi Transport Corporation",
        "description": "Public bus transportation services",
        "contact": {
            "email": "dtc@delhi.gov.in",
            "phone": "1800-11-0001"
        }
    }
]

# Categories mapped to departments
CATEGORIES = {
    "MCD": [
        {"name": "Garbage Collection", "description": "Issues related to garbage collection and disposal"},
        {"name": "Sanitation", "description": "Street cleaning and sanitation issues"},
        {"name": "Stray Animals", "description": "Stray dogs, cattle, and other animals"},
        {"name": "Waste Management", "description": "Illegal dumping and waste segregation"},
    ],
    "NDMC": [
        {"name": "Street Lights", "description": "Street light maintenance and repairs"},
        {"name": "Roads and Footpaths", "description": "Road and footpath maintenance"},
        {"name": "Parks and Gardens", "description": "Park maintenance and beautification"},
        {"name": "Water Logging", "description": "Drainage and water logging issues"},
    ],
    "PWD": [
        {"name": "Road Maintenance", "description": "Potholes, road repairs, and resurfacing"},
        {"name": "Bridges and Flyovers", "description": "Bridge and flyover maintenance"},
        {"name": "Traffic Infrastructure", "description": "Traffic signals and road markings"},
        {"name": "Drainage", "description": "Road drainage and water management"},
    ],
    "DDA": [
        {"name": "Land Management", "description": "Land use and encroachment issues"},
        {"name": "Building Violations", "description": "Unauthorized construction"},
        {"name": "Parks and Green Areas", "description": "DDA park and green area management"},
        {"name": "Housing", "description": "DDA housing and flat issues"},
    ],
    "DMRC": [
        {"name": "Metro Infrastructure", "description": "Escalators, elevators, and facilities"},
        {"name": "Metro Services", "description": "Train delays and service issues"},
        {"name": "Station Cleanliness", "description": "Station maintenance and cleanliness"},
        {"name": "Customer Service", "description": "Staff behavior and ticketing issues"},
    ],
    "DTC": [
        {"name": "Bus Services", "description": "Bus timing and route issues"},
        {"name": "Bus Stops", "description": "Bus stop infrastructure and maintenance"},
        {"name": "Bus Condition", "description": "Bus cleanliness and AC issues"},
        {"name": "Driver/Conductor Behavior", "description": "Staff conduct and behavior"},
    ]
}


async def initialize_database():
    """Initialize database with departments and categories."""
    print("Connecting to MongoDB...")
    client = AsyncIOMotorClient(MONGODB_URI, tlsAllowInvalidCertificates=True)
    db = client.nagrik
    
    try:
        # Clear existing departments and categories
        print("Clearing existing departments and categories...")
        await db.departments.delete_many({})
        await db.categories.delete_many({})
        
        dept_map = {}  # Map department name to ID
        
        # Create departments
        print("\nCreating departments...")
        for dept_data in DEPARTMENTS:
            result = await db.departments.insert_one(dept_data)
            dept_id = result.inserted_id
            dept_map[dept_data["name"]] = dept_id
            print(f"  ✓ Created: {dept_data['name']} - {dept_data['full_name']}")
        
        # Create categories
        print("\nCreating categories...")
        category_count = 0
        for dept_name, categories in CATEGORIES.items():
            dept_id = dept_map[dept_name]
            print(f"\n  {dept_name}:")
            
            for cat_data in categories:
                cat_data["default_department_id"] = dept_id
                result = await db.categories.insert_one(cat_data)
                category_count += 1
                print(f"    ✓ {cat_data['name']}")
        
        # Verify
        print("\n" + "="*60)
        print("Database initialization complete!")
        print("="*60)
        
        dept_count = await db.departments.count_documents({})
        cat_count = await db.categories.count_documents({})
        
        print(f"Total departments: {dept_count}")
        print(f"Total categories: {cat_count}")
        
        # Show department IDs
        print("\nDepartment IDs:")
        async for dept in db.departments.find({}):
            print(f"  {dept['name']:10} - {dept['_id']}")
        
    finally:
        client.close()
        print("\nDatabase connection closed.")


if __name__ == "__main__":
    asyncio.run(initialize_database())
