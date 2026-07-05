# main.py 
from fastapi import FastAPI 
from app.api.v1 import api_router 
 
app = FastAPI(title="Beauty Platform API", version="1.0.0") 
 
app.include_router(api_router, prefix="/api/v1") 
 
@app.get("/") 
async def root(): 
    return {"message": "Welcome to Beauty Platform API"} 
 
if __name__ == "__main__": 
    import uvicorn 
    uvicorn.run(app, host="0.0.0.0", port=8000) 
