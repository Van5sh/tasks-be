import os
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

load_dotenv()

_client = None

def get_client()-> AsyncIOMotorClient:
    global _client
    if _client is None:
        _client = AsyncIOMotorClient(os.getenv("MONGODB_URI"))
    return _client

def get_db():
    client = get_client()
    db_name = os.getenv("MONGODB_DB", "tasks_db")
    return client[db_name]


async def init_db():
    db = get_db()
    existing_collections = await db.list_collection_names()

    if "users" not in existing_collections:
        await db.create_collection("users")

    if "tasks" not in existing_collections:
        await db.create_collection("tasks")

    await db.users.create_index("email", unique=True)
    await db.tasks.create_index("user_id")
