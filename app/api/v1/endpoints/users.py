from fastapi import APIRouter, HTTPException, Depends 
from typing import List 
 
router = APIRouter(prefix="/users", tags=["users"]) 
 
@router.get("/") 
async def get_users(): 
    return [{"id": 1, "name": "Example User"}] 
 
@router.get("/{user_id}") 
async def get_user(user_id: int): 
    return {"id": user_id, "name": f"User {user_id}"} 
