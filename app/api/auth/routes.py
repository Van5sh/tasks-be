from fastapi import APIRouter, Depends, HTTPException
from pymongo.errors import DuplicateKeyError
from app.services.auth_service import register_user, login_user
from app.db.database import get_db
from app.models.user import UserCreate, UserLogin

router = APIRouter()

@router.post("/register")
async def register(user: UserCreate, db=Depends(get_db)):
    try:
        result = await register_user(db, user)
    except DuplicateKeyError:
        raise HTTPException(status_code=400, detail="Email already registered")
    if result.get("error"):
        raise HTTPException(status_code=400, detail=result["error"])
    return result

@router.post("/login")
async def login(user: UserLogin, db=Depends(get_db)):
    result = await login_user(db, user)
    
    if not result:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    return result
