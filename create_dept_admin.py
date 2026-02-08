import asyncio
from app.api.core.database import connect_db, get_db
from app.api.services.users import hash_password
from datetime import datetime, timezone

async def create_dept_admin():
    await connect_db()
    db = get_db()
    
    # Check if user exists
    phone = "9876543211"
    existing = await db.users.find_one({"phone": phone})
    
    if existing:
        print(f"User with phone {phone} already exists.")
        return

    now = datetime.now(timezone.utc)
    user_doc = {
        "name": "MCD Admin",
        "phone": phone,
        "password_hash": hash_password("mcd123"),
        "role": "department_admin",
        "department_id": "mcd",
        "created_at": now,
        "updated_at": now
    }
    
    result = await db.users.insert_one(user_doc)
    print(f"Department admin created: {result.inserted_id}")

if __name__ == "__main__":
    asyncio.run(create_dept_admin())
