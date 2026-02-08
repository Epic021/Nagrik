import asyncio
from app.api.core.database import connect_db, close_db, get_db
from app.api.services.users import hash_password, verify_password
from datetime import datetime, timezone

async def update_and_check():
    await connect_db()
    db = get_db()
    
    # Update test citizen password
    result = await db.users.update_one(
        {'phone': '9876543210'},
        {'$set': {
            'password_hash': hash_password('citizen123'),
            'updated_at': datetime.now(timezone.utc)
        }}
    )
    if result.modified_count > 0:
        print('✅ Test citizen password updated to: citizen123')
    else:
        print('⚠️  Test citizen already has this password or not found')
    
    # Check if MCD admin exists
    mcd_admin = await db.users.find_one({'phone': '9876543211'})
    if mcd_admin:
        print(f'\n✅ MCD Admin exists:')
        print(f'   Name: {mcd_admin["name"]}')
        print(f'   Phone: {mcd_admin["phone"]}')
        print(f'   Role: {mcd_admin["role"]}')
        print(f'   Department: {mcd_admin.get("department_id")}')
        
        # Test password
        if verify_password("mcd123", mcd_admin["password_hash"]):
            print('   ✅ Password "mcd123" is CORRECT')
        else:
            print('   ❌ Password "mcd123" is WRONG')
    else:
        print('\n❌ MCD Admin (9876543211) does NOT exist!')
        print('   Creating it now...')
        await db.users.insert_one({
            "name": "MCD Admin",
            "phone": "9876543211",
            "password_hash": hash_password("mcd123"),
            "role": "department_admin",
            "department_id": "mcd",
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc)
        })
        print('   ✅ MCD Admin created!')
        print('   Phone: 9876543211')
        print('   Password: mcd123')
        print('   Department: mcd')
    
    await close_db()

if __name__ == "__main__":
    asyncio.run(update_and_check())
