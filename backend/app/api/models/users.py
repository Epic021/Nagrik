from datetime import datetime
from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field


class UserRole(str, Enum):
    CITIZEN = "citizen"
    DEPARTMENT_ADMIN = "department_admin"
    SUPER_ADMIN = "super_admin"


class Location(BaseModel):
    lat: float = Field(..., ge=-90, le=90)
    lng: float = Field(..., ge=-180, le=180)
    address: Optional[str] = None


class UserBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    phone: str = Field(..., pattern=r"^[6-9]\d{9}$")  # Indian mobile
    email: Optional[str] = None
    location: Optional[Location] = None


class UserCreate(UserBase):
    password: str = Field(..., min_length=6)


class UserLogin(BaseModel):
    phone: str
    password: str


class UserInDB(UserBase):
    id: str
    password_hash: str
    role: UserRole = UserRole.CITIZEN
    department_id: Optional[str] = None  # For department admins
    created_at: datetime
    updated_at: datetime


class UserResponse(BaseModel):
    id: str
    name: str
    phone: str
    email: Optional[str] = None
    role: UserRole
    department_id: Optional[str] = None
    created_at: datetime


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse
