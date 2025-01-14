from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from app.core.config import settings

class MongoDB:
    client: AsyncIOMotorClient = None
    db: AsyncIOMotorDatabase = None

    @classmethod
    async def connect(cls):
        cls.client = AsyncIOMotorClient(
            settings.config["mongodb"]["uri"],
            maxPoolSize=settings.config["mongodb"]["max_pool_size"],
            minPoolSize=settings.config["mongodb"]["min_pool_size"],
            serverSelectionTimeoutMS=settings.config["mongodb"]["timeout_ms"]
        )
        
        cls.db = cls.client[settings.config["mongodb"]["database"]]

    @classmethod
    async def close(cls):
        if cls.client:
            cls.client.close()