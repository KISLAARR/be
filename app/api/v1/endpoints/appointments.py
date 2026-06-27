from fastapi import APIRouter 
 
router = APIRouter(prefix="/appointments", tags=["appointments"]) 
 
@router.get("/") 
async def get_appointments(): 
    return [{"id": 1, "date": "2024-01-01", "service": "Haircut"}] 
