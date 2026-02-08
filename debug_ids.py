"""Check department ID mismatch between complaints and route queries."""
import asyncio, os
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
load_dotenv()

async def check():
    client = AsyncIOMotorClient(os.getenv('MONGODB_URI'), tlsAllowInvalidCertificates=True)
    db = client.nagrik
    
    # Check a complaint's department.id format
    c = await db.complaints.find_one({})
    print("Sample complaint department:", c['department'])
    print("department.id type:", type(c['department']['id']))
    
    # Check admin user department_id
    admin = await db.users.find_one({'role': 'department_admin'})
    print()
    print("Admin name:", admin['name'])
    print("Admin department_id:", admin.get('department_id'))
    print("Admin department_id type:", type(admin.get('department_id')))
    
    # Check what the leaderboard queries
    dept_id = c['department']['id']
    count_by_objectid = await db.complaints.count_documents({'department.id': dept_id})
    count_by_mcd = await db.complaints.count_documents({'department.id': 'mcd'})
    print()
    print(f"Complaints matching stored dept id ({dept_id}): {count_by_objectid}")
    print(f"Complaints matching 'mcd': {count_by_mcd}")
    
    # Show all unique department.id values in complaints
    dept_ids = await db.complaints.distinct('department.id')
    print()
    print("Unique department.id in complaints:", dept_ids)
    
    # Show all unique department_id values in admin users
    user_dept_ids = await db.users.distinct('department_id')
    print("Unique department_id in users:", user_dept_ids)
    
    client.close()

asyncio.run(check())
