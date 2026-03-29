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
