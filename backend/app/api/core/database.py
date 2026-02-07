from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from .config import get_settings

settings = get_settings()

_client: AsyncIOMotorClient | None = None
_db: AsyncIOMotorDatabase | None = None
_db_connected: bool = False


async def connect_db():
    """Connect to MongoDB and create indexes. Gracefully handles missing DB."""
    global _client, _db, _db_connected
    
    try:
        _client = AsyncIOMotorClient(
            settings.MONGODB_URI,
            serverSelectionTimeoutMS=5000  # 5 second timeout
        )
        # Test connection
        await _client.admin.command('ping')
        _db = _client[settings.MONGODB_DB_NAME]
        
        # Create indexes for efficient queries
        await _db.complaints.create_index([("geo_location", "2dsphere")])
        await _db.complaints.create_index("category.id")
        await _db.complaints.create_index("department.id")
        await _db.complaints.create_index("status")
        await _db.complaints.create_index("upvote_count")
        await _db.complaints.create_index("created_at")
        await _db.users.create_index("phone", unique=True)
        
        _db_connected = True
        print(f"[OK] Connected to MongoDB: {settings.MONGODB_DB_NAME}")
    except Exception as e:
        _db_connected = False
        print(f"[WARN] MongoDB not available: {e}")
        print("   Static routes will work. DB routes will return errors.")
        print("   To start MongoDB: docker run -d -p 27017:27017 mongo:latest")


async def close_db():
    """Close MongoDB connection."""
    global _client, _db_connected
    if _client:
        _client.close()
        _db_connected = False
        print("MongoDB connection closed")


def get_db() -> AsyncIOMotorDatabase:
    """Get database instance."""
    if not _db_connected or _db is None:
        raise RuntimeError("Database not connected. Start MongoDB or use a cloud instance.")
    return _db


def is_db_connected() -> bool:
    """Check if database is connected."""
    return _db_connected
