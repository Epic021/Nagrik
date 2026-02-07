from datetime import datetime, timedelta, timezone
from typing import Optional

import bcrypt
from jose import jwt
from bson import ObjectId

from ..core.config import get_settings
from ..core.database import get_db
from ..models.users import UserCreate, UserInDB, UserResponse, UserRole

settings = get_settings()


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(plain_password.encode(), hashed_password.encode())


def create_access_token(user_id: str) -> str:
    expire = datetime.now(timezone.utc) + timedelta(hours=settings.JWT_EXPIRY_HOURS)
    payload = {
        "sub": user_id,
        "exp": expire,
        "iat": datetime.now(timezone.utc)
    }
    return jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def decode_token(token: str) -> Optional[str]:
    """Decode JWT token and return user_id, or None if invalid."""
    try:
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        return payload.get("sub")
    except jwt.JWTError:
        return None


async def create_user(user_data: UserCreate) -> UserResponse:
    """Create a new user."""
    db = get_db()
    now = datetime.now(timezone.utc)
    
    user_doc = {
        "name": user_data.name,
        "phone": user_data.phone,
        "email": user_data.email,
        "password_hash": hash_password(user_data.password),
        "role": UserRole.CITIZEN.value,
        "department_id": None,
        "location": user_data.location.model_dump() if user_data.location else None,
        "created_at": now,
        "updated_at": now
    }
    
    result = await db.users.insert_one(user_doc)
    
    return UserResponse(
        id=str(result.inserted_id),
        name=user_data.name,
        phone=user_data.phone,
        email=user_data.email,
        role=UserRole.CITIZEN,
        created_at=now
    )


async def get_user_by_phone(phone: str) -> Optional[dict]:
    """Get user by phone number."""
    db = get_db()
    return await db.users.find_one({"phone": phone})


async def get_user_by_id(user_id: str) -> Optional[dict]:
    """Get user by ID."""
    db = get_db()
    try:
        return await db.users.find_one({"_id": ObjectId(user_id)})
    except:
        return None


async def authenticate_user(phone: str, password: str) -> Optional[dict]:
    """Authenticate user by phone and password."""
    user = await get_user_by_phone(phone)
    if not user:
        return None
    if not verify_password(password, user["password_hash"]):
        return None
    return user


def user_doc_to_response(user_doc: dict) -> UserResponse:
    """Convert MongoDB user document to response model."""
    return UserResponse(
        id=str(user_doc["_id"]),
        name=user_doc["name"],
        phone=user_doc["phone"],
        email=user_doc.get("email"),
        role=UserRole(user_doc["role"]),
        created_at=user_doc["created_at"]
    )
