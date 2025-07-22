import asyncio
import os

import motor
from motor.motor_asyncio import AsyncIOMotorClient

async def ensure_indexes(retries: int = 10, delay: float = 2):
    for i in range(retries):
        try:
            cli = motor.motor_asyncio.AsyncIOMotorClient(os.getenv("MONGO_URI"))
            col = cli["catalog_db"]["products"]
            await col.create_index("name", unique=True)
            await col.create_index([("category", 1), ("active", 1)])
            return
        except Exception as e:
            if i == retries - 1:
                raise
            await asyncio.sleep(delay)

