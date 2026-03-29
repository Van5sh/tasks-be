def get_user(db, user_id):
    return db["users"].find_one({"_id": user_id})

def create_user(db, user_data):
    return db["users"].insert_one(user_data)

def update_user(db, user_id, update_data):
    return db["users"].update_one({"_id": user_id}, {"$set": update_data})

def delete_user(db, user_id):
    return db["users"].delete_one({"_id": user_id})
