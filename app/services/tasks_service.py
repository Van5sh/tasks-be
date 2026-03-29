def getTasks(db,user_id):
    return db["tasks"].find({"user_id": user_id})
    