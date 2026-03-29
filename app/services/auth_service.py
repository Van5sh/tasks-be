from app.config.security import hash_password, verify_password, create_access_token

def _model_dump(model):
    return model.model_dump() if hasattr(model, "model_dump") else model.dict()


async def register_user(db, user):
    user_dict = _model_dump(user)
    user_dict["password"] = hash_password(user.password)

    await db.users.insert_one(user_dict)

    return {"message": "User created"}


async def login_user(db, user):
    db_user = await db.users.find_one({"email": user.email})

    if not db_user:
        return None

    if not verify_password(user.password, db_user["password"]):
        return None

    token = create_access_token({"sub": str(db_user["_id"])})

    return {"access_token": token, "token_type": "bearer"}
