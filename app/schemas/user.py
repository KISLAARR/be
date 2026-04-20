# app/schemas/user.py
from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime
from app.models.models import UserRole, SubscriptionTier

class UserBase(BaseModel):
    phone: str
    full_name: Optional[str] = None
    email: Optional[EmailStr] = None

class UserCreate(UserBase):
    password: str = Field(..., min_length=6)
    role: UserRole = UserRole.CLIENT

class UserResponse(UserBase):
    id: int
    role: UserRole
    avatar_url: Optional[str] = None
    subscription_tier: Optional[SubscriptionTier] = None
    subscription_expires_at: Optional[datetime] = None
    created_at: datetime
    
    class Config:
        from_attributes = True

class UserLogin(BaseModel):
    phone: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"