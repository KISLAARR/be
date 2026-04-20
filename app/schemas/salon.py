# app/schemas/salon.py
from pydantic import BaseModel
from typing import Optional, List

class SalonBase(BaseModel):
    name: str
    description: Optional[str] = None
    address: str
    latitude: float
    longitude: float
    phone: str

class SalonCreate(SalonBase):
    pass

class SalonResponse(SalonBase):
    id: int
    logo_url: Optional[str] = None
    rating: float
    reviews_count: int
    working_hours: Optional[str] = None
    is_active: bool
    
    class Config:
        from_attributes = True

class SalonWithDistance(SalonResponse):
    distance_km: float