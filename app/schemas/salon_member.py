# app/schemas/salon_member.py
from pydantic import BaseModel
from typing import Optional, Dict
from datetime import datetime

from app.models.models import SalonRole


class SalonMemberUserResponse(BaseModel):
    id: int
    full_name: Optional[str] = None
    phone: str

    class Config:
        from_attributes = True


class SalonMemberResponse(BaseModel):
    id: int
    role: SalonRole
    is_creator: bool
    permissions: Dict[str, bool]
    is_active: bool
    created_at: datetime
    user: SalonMemberUserResponse

    class Config:
        from_attributes = True


class UpdatePermissionsRequest(BaseModel):
    permissions: Dict[str, bool]
