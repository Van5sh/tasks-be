from fastapi import APIRouter, Depends, HTTPException
from app.dependency.auth import get_current_user
from app.db.database import get_db

router = APIRouter()


@router.get("/users/me")
async def me(user=Depends(get_current_user)):
    return {"id": user["sub"], "role": user.get("role", "user")}


@router.get("/admin/users")
async def list_users(db=Depends(get_db), user=Depends(get_current_user)):
    if user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Forbidden")
    cursor = db.users.find({}, {"password": 0})
    users = []
    async for u in cursor:
        u["id"] = str(u.pop("_id"))
        users.append(u)
    return users
