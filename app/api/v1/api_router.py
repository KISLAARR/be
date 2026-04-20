from fastapi import APIRouter 
from app.api.v1.endpoints import users, services, appointments 
 
api_router = APIRouter() 
 
api_router.include_router(users.router) 
api_router.include_router(services.router) 
api_router.include_router(appointments.router) 
