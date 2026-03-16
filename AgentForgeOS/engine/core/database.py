from motor.motor_asyncio import AsyncIOMotorClient
from pathlib import Path
from dotenv import load_dotenv
import os

OS_ROOT = Path(__file__).parent.parent.parent
load_dotenv(OS_ROOT / "config" / ".env")

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

async def shutdown_db():
    client.close()
