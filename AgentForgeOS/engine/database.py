"""
Database bootstrap
"""

from motor.motor_asyncio import AsyncIOMotorClient
from engine.config import get_setting


mongo_url = get_setting("MONGO_URL", "mongodb://localhost:27017")
db_name = get_setting("DB_NAME", "agentforge")
client = AsyncIOMotorClient(mongo_url)
db = client[db_name]


async def shutdown_db():
    client.close()
