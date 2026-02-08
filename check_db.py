"""Check database collections."""
import asyncio
import os
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

load_dotenv()

async def check():
    client = AsyncIOMotorClient(os.getenv('MONGODB_URI'), tlsAllowInvalidCertificates=True)
    db = client.nagrik
    
    depts = await db.departments.find({}).to_list(100)
    print(f'Departments: {len(depts)}')
    for d in depts:
        print(f"  - {d['name']} (ID: {d['_id']})")
    
    cats = await db.categories.find({}).to_list(100)
    print(f'\nCategories: {len(cats)}')
    for c in cats[:5]:
        print(f"  - {c['name']} -> Dept ID: {c.get('default_department_id', 'None')}")
    
    users = await db.users.find({}).to_list(100)
    print(f'\nUsers: {len(users)}')
    
    complaints = await db.complaints.count_documents({})
    print(f'\nComplaints: {complaints}')
    
    client.close()

asyncio.run(check())
