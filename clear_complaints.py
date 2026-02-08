"""
Clear all complaints from the database
"""
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv

load_dotenv()

async def clear_complaints():
    mongodb_uri = os.getenv("MONGODB_URI")
    client = AsyncIOMotorClient(mongodb_uri, tlsAllowInvalidCertificates=True)
    db = client.nagrik
    
    # Count existing complaints
    count = await db.complaints.count_documents({})
    print(f"Found {count} complaints in database")
    
    if count > 0:
        # Delete all complaints
        result = await db.complaints.delete_many({})
        print(f"✓ Deleted {result.deleted_count} complaints")
    else:
        print("✓ No complaints to delete")
    
    print(f"\n{'='*60}")
    print("Database cleared successfully")
    print(f"{'='*60}")
    
    client.close()

if __name__ == "__main__":
    asyncio.run(clear_complaints())
