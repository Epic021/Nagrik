"""
Create multiple department admins for testing
"""
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import bcrypt
import os
from datetime import datetime, timezone
from dotenv import load_dotenv

load_dotenv()

def hash_password(password: str) -> str:
    """Hash a password using bcrypt"""
    pwd_bytes = password.encode('utf-8')
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(pwd_bytes, salt)
    return hashed.decode('utf-8')

async def create_department_admins():
    # Connect to MongoDB
    mongodb_uri = os.getenv("MONGODB_URI")
    client = AsyncIOMotorClient(mongodb_uri, tlsAllowInvalidCertificates=True)
    db = client.nagrik
    
    # Department admins to create
    dept_admins = [
        {
            "phone": "9876543211",
            "password": "mcd123",
            "name": "MCD Admin",
            "email": "mcd@delhi.gov.in",
            "role": "department_admin",
            "department_id": "mcd",
            "department_name": "Municipal Corporation of Delhi"
        },
        {
            "phone": "9876543212",
            "password": "ndmc123",
            "name": "NDMC Admin",
            "email": "ndmc@delhi.gov.in",
            "role": "department_admin",
            "department_id": "ndmc",
            "department_name": "New Delhi Municipal Council"
        },
        {
            "phone": "9876543213",
            "password": "pwd123",
            "name": "PWD Admin",
            "email": "pwd@delhi.gov.in",
            "role": "department_admin",
            "department_id": "pwd",
            "department_name": "Public Works Department"
        },
        {
            "phone": "9876543214",
            "password": "dda123",
            "name": "DDA Admin",
            "email": "dda@delhi.gov.in",
            "role": "department_admin",
            "department_id": "dda",
            "department_name": "Delhi Development Authority"
        },
        {
            "phone": "9876543215",
            "password": "dmrc123",
            "name": "DMRC Admin",
            "email": "dmrc@delhi.gov.in",
            "role": "department_admin",
            "department_id": "dmrc",
            "department_name": "Delhi Metro Rail Corporation"
        },
        {
            "phone": "9876543216",
            "password": "dtc123",
            "name": "DTC Admin",
            "email": "dtc@delhi.gov.in",
            "role": "department_admin",
            "department_id": "dtc",
            "department_name": "Delhi Transport Corporation"
        }
    ]
    
    created = []
    updated = []
    
    for admin in dept_admins:
        phone = admin["phone"]
        
        # Check if user exists
        existing = await db.users.find_one({"phone": phone})
        
        # Hash password
        hashed_password = hash_password(admin["password"])
        
        now = datetime.now(timezone.utc)
        
        user_data = {
            "phone": phone,
            "password_hash": hashed_password,
            "name": admin["name"],
            "email": admin["email"],
            "role": admin["role"],
            "department_id": admin["department_id"],
            "is_active": True,
            "created_at": now,
            "updated_at": now
        }
        
        if existing:
            # Update existing user
            await db.users.update_one(
                {"phone": phone},
                {"$set": user_data}
            )
            updated.append(f"{admin['name']} ({phone}) - {admin['department_name']}")
            print(f"✓ Updated: {admin['name']} ({phone}) - {admin['department_name']}")
        else:
            # Create new user
            await db.users.insert_one(user_data)
            created.append(f"{admin['name']} ({phone}) - {admin['department_name']}")
            print(f"✓ Created: {admin['name']} ({phone}) - {admin['department_name']}")
    
    print(f"\n{'='*60}")
    print(f"Summary:")
    print(f"{'='*60}")
    print(f"Created: {len(created)} admins")
    print(f"Updated: {len(updated)} admins")
    print(f"\nAll department admins:")
    for admin in dept_admins:
        print(f"  • {admin['name']} ({admin['phone']}) - Password: {admin['password']}")
    
    client.close()

if __name__ == "__main__":
    asyncio.run(create_department_admins())
