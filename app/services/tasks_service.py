from datetime import datetime
from bson import ObjectId


def _is_owner(task: dict, user_id: str) -> bool:
    return task.get("owner_id", task.get("user_id")) == user_id


def _has_access(task: dict, user_id: str) -> bool:
    if _is_owner(task, user_id):
        return True
    invited_users = task.get("invited_users", [])
    return any(invited_user.get("user_id") == user_id for invited_user in invited_users)


def _serialize_task(task: dict, user_id: str) -> dict:
    invited_users = [
        {
            "user_id": invited_user["user_id"],
            "email": invited_user["email"],
            "access": invited_user.get("access", "normal"),
        }
        for invited_user in task.get("invited_users", [])
    ]
    return {
        "id": str(task["_id"]),
        "title": task["title"],
        "description": task.get("description"),
        "completed": task.get("completed", False),
        "owner_id": task.get("owner_id", task.get("user_id")),
        "access": "admin" if _is_owner(task, user_id) else "normal",
        "invited_users": invited_users,
        "created_at": task.get("created_at"),
        "updated_at": task.get("updated_at"),
    }


def _oid(task_id: str) -> ObjectId:
    return ObjectId(task_id)


async def create_task(db, user_id: str, task):
    now = datetime.utcnow()
    payload = task.model_dump() if hasattr(task, "model_dump") else task.dict()
    payload.update(
        {
            "owner_id": user_id,
            "user_id": user_id,
            "invited_users": [],
            "created_at": now,
            "updated_at": now,
        }
    )
    result = await db.tasks.insert_one(payload)
    created = await db.tasks.find_one({"_id": result.inserted_id})
    return _serialize_task(created, user_id)


async def list_tasks(db, user_id: str, skip: int = 0, limit: int = 50):
    cursor = (
        db.tasks.find(
            {
                "$or": [
                    {"owner_id": user_id},
                    {"user_id": user_id},
                    {"invited_users.user_id": user_id},
                ]
            }
        )
        .skip(skip)
        .limit(limit)
    )
    tasks = []
    async for task in cursor:
        tasks.append(_serialize_task(task, user_id))
    return tasks


async def get_task(db, user_id: str, task_id: str):
    task = await db.tasks.find_one({"_id": _oid(task_id)})
    if not task or not _has_access(task, user_id):
        return None
    return _serialize_task(task, user_id)


async def update_task(db, user_id: str, task_id: str, task):
    existing = await db.tasks.find_one({"_id": _oid(task_id)})
    if not existing or not _has_access(existing, user_id):
        return None
    payload = task.model_dump(exclude_unset=True) if hasattr(task, "model_dump") else task.dict(exclude_unset=True)
    payload["updated_at"] = datetime.utcnow()
    result = await db.tasks.update_one(
        {"_id": _oid(task_id)},
        {"$set": payload},
    )
    if result.matched_count == 0:
        return None
    updated = await db.tasks.find_one({"_id": _oid(task_id)})
    return _serialize_task(updated, user_id)


async def delete_task(db, user_id: str, task_id: str):
    result = await db.tasks.delete_one(
        {
            "_id": _oid(task_id),
            "$or": [{"owner_id": user_id}, {"user_id": user_id}],
        }
    )
    return result.deleted_count == 1


async def invite_user_to_task(db, owner_id: str, task_id: str, email: str):
    task = await db.tasks.find_one({"_id": _oid(task_id)})
    if not task or not _is_owner(task, owner_id):
        return None

    user = await db.users.find_one({"email": email})
    if not user:
        return {"error": "User not found"}

    invited_user_id = str(user["_id"])
    if invited_user_id == owner_id:
        return {"error": "Task owner already has admin access"}

    invited_users = task.get("invited_users", [])
    if any(invited_user.get("user_id") == invited_user_id for invited_user in invited_users):
        return {"error": "User already invited"}

    invitation = {
        "user_id": invited_user_id,
        "email": user["email"],
        "access": "normal",
    }
    await db.tasks.update_one(
        {"_id": _oid(task_id)},
        {
            "$push": {"invited_users": invitation},
            "$set": {"updated_at": datetime.utcnow()},
        },
    )
    updated = await db.tasks.find_one({"_id": _oid(task_id)})
    return _serialize_task(updated, owner_id)
