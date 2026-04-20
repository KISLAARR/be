from fastapi import APIRouter 
 
router = APIRouter(prefix="/services", tags=["services"]) 
 
@router.get("/") 
async def get_services(): 
    return [{"id": 1, "name": "Haircut", "price": 1000}] 
