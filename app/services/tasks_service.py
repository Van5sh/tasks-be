from datetime import datetime
from bson import ObjectId


def _serialize_task(task: dict) -> dict:
    return {
        "id": str(task["_id"]),
        "title": task["title"],
        "description": task.get("description"),
        "completed": task.get("completed", False),
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
            "user_id": user_id,
            "created_at": now,
            "updated_at": now,
        }
    )
    result = await db.tasks.insert_one(payload)
    created = await db.tasks.find_one({"_id": result.inserted_id})
    return _serialize_task(created)


async def list_tasks(db, user_id: str, skip: int = 0, limit: int = 50):
    cursor = db.tasks.find({"user_id": user_id}).skip(skip).limit(limit)
    tasks = []
    async for task in cursor:
        tasks.append(_serialize_task(task))
    return tasks


async def get_task(db, user_id: str, task_id: str):
    task = await db.tasks.find_one({"_id": _oid(task_id), "user_id": user_id})
    if not task:
        return None
    return _serialize_task(task)


async def update_task(db, user_id: str, task_id: str, task):
    payload = task.model_dump(exclude_unset=True) if hasattr(task, "model_dump") else task.dict(exclude_unset=True)
    payload["updated_at"] = datetime.utcnow()
    result = await db.tasks.update_one(
        {"_id": _oid(task_id), "user_id": user_id},
        {"$set": payload},
    )
    if result.matched_count == 0:
        return None
    updated = await db.tasks.find_one({"_id": _oid(task_id), "user_id": user_id})
    return _serialize_task(updated)


async def delete_task(db, user_id: str, task_id: str):
    result = await db.tasks.delete_one({"_id": _oid(task_id), "user_id": user_id})
    return result.deleted_count == 1
