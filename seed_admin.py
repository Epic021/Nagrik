
import asyncio
from app.api.core.database import connect_db, close_db, get_db
from app.api.services.users import hash_password, verify_password, get_user_by_phone
from datetime import datetime, timezone


async def seed_super_admin():
    """Create super admin."""
    await connect_db()
    
    try:
        db = get_db()
        
        # Check if super admin exists
        existing = await db.users.find_one({"phone": "9999999999"})
        
        if existing:
            print(f"✅ Super admin already exists:")
            print(f"   Name: {existing['name']}")
            print(f"   Phone: {existing['phone']}")
            print(f"   Role: {existing['role']}")
            
            # Test password
            if verify_password("admin123", existing["password_hash"]):
                print("   ✅ Password 'admin123' is CORRECT")
            else:
                print("   ❌ Password 'admin123' is WRONG - Resetting...")
                await db.users.update_one(
                    {"phone": "9999999999"},
                    {"$set": {
                        "password_hash": hash_password("admin123"),
                        "updated_at": datetime.now(timezone.utc)
                    }}
                )
                print("   ✅ Password reset to 'admin123'")
        else:
            print("Creating new super admin...")
            await db.users.insert_one({
                "name": "Super Admin",
                "phone": "9999999999",
                "password_hash": hash_password("admin123"),
                "role": "super_admin",
                "department_id": None,
                "created_at": datetime.now(timezone.utc),
                "updated_at": datetime.now(timezone.utc)
            })
            print("✅ Super admin created successfully!")
            print("   Phone: 9999999999")
            print("   Password: admin123")
        
        # Also check/create a test citizen
        citizen = await db.users.find_one({"phone": "9876543210"})
        if not citizen:
            print("\nCreating test citizen user...")
            await db.users.insert_one({
                "name": "Test User",
                "phone": "9876543210",
                "password_hash": hash_password("test123"),
                "role": "citizen",
                "department_id": None,
                "created_at": datetime.now(timezone.utc),
                "updated_at": datetime.now(timezone.utc)
            })
            print("✅ Test citizen created!")
            print("   Phone: 9876543210")
            print("   Password: test123")
        
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        await close_db()


if __name__ == "__main__":
    asyncio.run(seed_super_admin())
