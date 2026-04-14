from datetime import timedelta
from app.config.security import hash_password, verify_password, create_access_token, ACCESS_TOKEN_EXPIRE_MINUTES

def _model_dump(model):
    if hasattr(model, "model_dump"):
        return model.model_dump(mode="json")
    return model.dict()


async def register_user(db, user):
    user_dict = _model_dump(user)
    user_dict["password"] = hash_password(user.password)
    user_dict["role"] = "user"

    existing = await db.users.find_one({"email": user.email})
    if existing:
        return {"error": "Email already registered"}

    await db.users.insert_one(user_dict)

    return {"message": "User created"}


async def login_user(db, user):
    db_user = await db.users.find_one({"email": user.email})

    if not db_user:
        return None

    if not verify_password(user.password, db_user["password"]):
        return None

    token = create_access_token(
        {"sub": str(db_user["_id"]), "role": db_user.get("role", "user")},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
    )

    return {"access_token": token, "token_type": "bearer"}
