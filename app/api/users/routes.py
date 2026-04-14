from fastapi import APIRouter, Depends, HTTPException
from bson import ObjectId
from app.dependency.auth import get_current_user
from app.db.database import get_db

router = APIRouter()


@router.get("/users/me")
async def me(db=Depends(get_db), user=Depends(get_current_user)):
    """
    Return the authenticated user's profile details.

    Frontend expects `username`, `email`, `dob`, and `gender` to be present.
    """
    user_id = user.get("sub")
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid token payload")

    try:
        oid = ObjectId(user_id)
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid token subject")

    db_user = await db.users.find_one({"_id": oid}, {"password": 0})
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    db_user["id"] = str(db_user.pop("_id"))
    # Ensure role exists even if older records don't have it.
    db_user.setdefault("role", user.get("role", "user"))
    return db_user


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
