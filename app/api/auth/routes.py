from fastapi import APIRouter, Depends, HTTPException
from app.services.auth_service import register_user, login_user
from app.db.database import get_db
from app.models.user import UserCreate, UserLogin

router = APIRouter()

@router.post("/register")
async def register(user: UserCreate, db=Depends(get_db)):
    return await register_user(db, user)

@router.post("/login")
async def login(user: UserLogin, db=Depends(get_db)):
    result = await login_user(db, user)
    
    if not result:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    return result
