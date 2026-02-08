"""
Fix all users to use password_hash field
"""
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import bcrypt
import os
from dotenv import load_dotenv

load_dotenv()

def hash_password(password: str) -> str:
    """Hash a password using bcrypt"""
    pwd_bytes = password.encode('utf-8')
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(pwd_bytes, salt)
    return hashed.decode('utf-8')

async def fix_users():
    # Connect to MongoDB
    mongodb_uri = os.getenv("MONGODB_URI")
    client = AsyncIOMotorClient(mongodb_uri, tlsAllowInvalidCertificates=True)
    db = client.nagrik
    
    # Find all users with 'password' field instead of 'password_hash'
    users_to_fix = await db.users.find({"password": {"$exists": True}}).to_list(None)
    
    print(f"Found {len(users_to_fix)} users to fix\n")
    
    for user in users_to_fix:
        # Move password to password_hash
        await db.users.update_one(
            {"_id": user["_id"]},
            {
                "$set": {"password_hash": user["password"]},
                "$unset": {"password": ""}
            }
        )
        print(f"✓ Fixed: {user.get('name', 'Unknown')} ({user.get('phone', 'N/A')})")
    
    print(f"\n{'='*60}")
    print(f"Fixed {len(users_to_fix)} users")
    print(f"{'='*60}")
    
    client.close()

if __name__ == "__main__":
    asyncio.run(fix_users())
