"""Fix admin users: update department_id from short codes to actual MongoDB ObjectIds."""
import asyncio, os
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
load_dotenv()

# Mapping: short department name -> admin phone
DEPT_SHORT_TO_PHONE = {
    "MCD": "9876543211",
    "NDMC": "9876543212",
    "PWD": "9876543213",
    "DDA": "9876543214",
    "DMRC": "9876543215",
    "DTC": "9876543216",
}

async def fix_admin_dept_ids():
    client = AsyncIOMotorClient(os.getenv('MONGODB_URI'), tlsAllowInvalidCertificates=True)
    db = client.nagrik

    # Get all departments from DB
    departments = await db.departments.find({}).to_list(100)
    print(f"Found {len(departments)} departments in DB\n")

    for dept in departments:
        dept_id = str(dept["_id"])
        dept_name = dept["name"]  # e.g. "MCD"
        phone = DEPT_SHORT_TO_PHONE.get(dept_name)

        if not phone:
            print(f"  SKIP: No admin mapped for department '{dept_name}'")
            continue

        # Update the admin user's department_id to the actual ObjectId string
        result = await db.users.update_one(
            {"phone": phone, "role": "department_admin"},
            {"$set": {"department_id": dept_id}}
        )

        if result.modified_count > 0:
            print(f"  FIXED: {dept_name} admin ({phone}) -> department_id = {dept_id}")
        else:
            # Check if already correct
            user = await db.users.find_one({"phone": phone})
            if user and user.get("department_id") == dept_id:
                print(f"  OK:    {dept_name} admin ({phone}) already has correct department_id")
            else:
                print(f"  WARN:  {dept_name} admin ({phone}) not found or not modified")

    # Verify
    print("\n--- Verification ---")
    admins = await db.users.find({"role": "department_admin"}).to_list(100)
    for admin in admins:
        dept_id = admin.get("department_id", "MISSING")
        # Look up department name
        dept = await db.departments.find_one({"_id": __import__('bson').ObjectId(dept_id)}) if len(dept_id) == 24 else None
        dept_label = dept["name"] if dept else f"(unknown: {dept_id})"
        print(f"  {admin['name']:15} phone={admin['phone']}  department_id={dept_id}  -> {dept_label}")

    # Also check: how many complaints does each admin's department have?
    print("\n--- Complaint counts per admin's department ---")
    for admin in admins:
        dept_id = admin.get("department_id")
        count = await db.complaints.count_documents({"department.id": dept_id})
        print(f"  {admin['name']:15} department_id={dept_id}  complaints={count}")

    client.close()

asyncio.run(fix_admin_dept_ids())
